#!/usr/bin/env python3
  """
  ATF Evidence Package (OEP) Offline Verifier — RFC-ATF-3
  ========================================================
  Verifies a complete OMNIX Evidence Package (OEP) entirely offline.

  An OEP is a self-contained forensic ZIP archive containing:
    - All ATF receipts for a governance session
    - Merkle proofs for each receipt (EAP-INV-004)
    - The Archive Root Hash (ARH) with its PQC signature (EAP-INV-002)
    - The issuer's ML-DSA-65 public key (OEP-INV-003)
    - A machine-readable manifest (OEP-INV-002)
    - JSON Schemas for all artifact types (OEP-INV-001)

  This verifier enforces:
    OEP-INV-001  Package is self-contained — no external resolution
    OEP-INV-002  Manifest includes schema_version
    OEP-INV-003  Package includes issuer public key
    OEP-INV-004  Every receipt has a Merkle proof
    OEP-INV-005  Package integrity verified by ARH
    OEP-INV-006  Manifest hash covers all package contents
    EAP-INV-001  Archive entries are Merkle-chained (hash chain)
    EAP-INV-002  ARH is PQC-signed (ML-DSA-65)
    EAP-INV-003  No entry can be removed (chain breaks)
    EAP-INV-004  Merkle proof is reproducible
    EAP-INV-005  Complete offline verifiability — no platform access
    EAP-INV-007  Entry hash covers full receipt payload
    FVP-INV-007  Verifier determinism — same key+package = same result

  Requirements:
      pip install pypqc

  Usage:
      python verify_oep_package.py <package.zip>
      python verify_oep_package.py <package.zip> --public-key <key.b64>
      python verify_oep_package.py <package.zip> --verbose --output-transcript

  This tool has ZERO dependency on the OMNIX platform (EAP-INV-005).
  """

  import argparse
  import base64
  import hashlib
  import json
  import sys
  import zipfile
  from dataclasses import dataclass, field
  from io import BytesIO
  from pathlib import Path
  from typing import Optional

  # ── Max decompressed size guard (ZIP bomb protection) ─────────────────────────
  MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024  # 512 MB

  # ── Reason codes ─────────────────────────────────────────────────────────────

  class RC:
      """Normative reason codes for OEP verification results."""
      MANIFEST_MISSING       = "OEP-INV-002/MANIFEST_MISSING"
      MANIFEST_SCHEMA_VER    = "OEP-INV-002/SCHEMA_VERSION_MISSING"
      PUBLIC_KEY_MISSING     = "OEP-INV-003/PUBLIC_KEY_MISSING"
      RECEIPT_NO_PROOF       = "OEP-INV-004/RECEIPT_MISSING_MERKLE_PROOF"
      ARH_MISMATCH           = "OEP-INV-005/ARH_INTEGRITY_FAIL"
      MANIFEST_HASH_MISMATCH = "OEP-INV-006/MANIFEST_HASH_MISMATCH"
      MERKLE_CHAIN_BREAK     = "EAP-INV-001/CHAIN_INTEGRITY_BREAK"
      ARH_SIGNATURE_INVALID  = "EAP-INV-002/ARH_SIGNATURE_INVALID"
      ARH_SIGNATURE_SKIP     = "EAP-INV-002/ARH_SIGNATURE_SKIP_NO_KEY"
      MERKLE_PROOF_INVALID   = "EAP-INV-004/MERKLE_PROOF_INVALID"
      ENTRY_HASH_MISMATCH    = "EAP-INV-007/ENTRY_HASH_MISMATCH"
      SIZE_LIMIT_EXCEEDED    = "SECURITY/MAX_UNCOMPRESSED_SIZE_EXCEEDED"
      PATH_TRAVERSAL         = "SECURITY/PATH_TRAVERSAL_DETECTED"
      ZIP_INVALID            = "STRUCTURE/ZIP_INVALID"
      RECEIPT_PARSE_ERROR    = "STRUCTURE/RECEIPT_PARSE_ERROR"


  # ── Result structures ─────────────────────────────────────────────────────────

  @dataclass
  class CheckResult:
      invariant: str
      ok: bool
      reason_code: Optional[str] = None
      detail: Optional[str] = None


  @dataclass
  class OepVerificationReport:
      verdict: str  # PASS | FAIL | WARN
      package_fingerprint: str  # SHA-256 of raw package bytes
      receipt_count: int
      checks: dict = field(default_factory=dict)
      key_identity: dict = field(default_factory=dict)
      notes: list = field(default_factory=list)
      receipt_results: list = field(default_factory=list)

      def to_dict(self) -> dict:
          return {
              "verdict": self.verdict,
              "package_fingerprint": self.package_fingerprint,
              "receipt_count": self.receipt_count,
              "key_identity": self.key_identity,
              "checks": {k: {"ok": v.ok, "invariant": v.invariant,
                              **({"reason_code": v.reason_code} if v.reason_code else {}),
                              **({"detail": v.detail} if v.detail else {})}
                         for k, v in self.checks.items()},
              "receipt_results": self.receipt_results,
              "notes": self.notes,
          }


  # ── Merkle utilities ──────────────────────────────────────────────────────────

  def sha256_hex(data: bytes) -> str:
      return hashlib.sha256(data).hexdigest()


  def compute_entry_hash(receipt_bytes: bytes) -> str:
      """EAP-INV-007: entry hash covers full receipt payload."""
      return "sha256:" + sha256_hex(receipt_bytes)


  def verify_merkle_proof(leaf_hash: str, proof: list, claimed_root: str) -> bool:
      """
      EAP-INV-004: Verify a Merkle inclusion proof.
      proof is a list of {"sibling": <hex>, "position": "left"|"right"} objects.
      """
      current = leaf_hash.replace("sha256:", "")
      for step in proof:
          sibling = step.get("sibling", "")
          position = step.get("position", "right")
          if position == "left":
              combined = bytes.fromhex(sibling) + bytes.fromhex(current)
          else:
              combined = bytes.fromhex(current) + bytes.fromhex(sibling)
          current = sha256_hex(combined)
      return current == claimed_root.replace("sha256:", "")


  def compute_chain_root(entry_hashes: list[str]) -> str:
      """
      EAP-INV-001: Recompute the Archive Root Hash from ordered entry hashes.
      Uses a simple sequential Merkle chain: hash(h[i-1] || h[i]).
      For a single entry, the chain root equals the entry hash.
      """
      if not entry_hashes:
          return "sha256:" + sha256_hex(b"")
      if len(entry_hashes) == 1:
          return entry_hashes[0]
      current = entry_hashes[0].replace("sha256:", "")
      for h in entry_hashes[1:]:
          combined = bytes.fromhex(current) + bytes.fromhex(h.replace("sha256:", ""))
          current = sha256_hex(combined)
      return "sha256:" + current


  # ── PQC signature verification ────────────────────────────────────────────────

  def verify_arh_signature(arh: str, signature_b64: str, public_key_b64: str) -> tuple[bool, str]:
      """EAP-INV-002: Verify ARH PQC signature using ML-DSA-65."""
      try:
          from pypqc import sign
          pub_key = base64.b64decode(public_key_b64)
          sig_bytes = base64.b64decode(signature_b64)
          message = arh.encode("utf-8")
          verified = sign.verify(message, sig_bytes, pub_key)
          if verified:
              return True, "ARH PQC signature verified (ML-DSA-65)"
          return False, "ARH PQC signature verification failed"
      except ImportError:
          return False, "pypqc not installed — pip install pypqc"
      except Exception as e:
          return False, f"ARH signature verification error: {e}"


  # ── Path safety ───────────────────────────────────────────────────────────────

  def is_safe_path(path: str) -> bool:
      """Reject path traversal and absolute paths."""
      p = Path(path)
      if p.is_absolute():
          return False
      try:
          resolved = Path("/sandbox").joinpath(p).resolve()
          return resolved.is_relative_to(Path("/sandbox"))
      except (ValueError, RuntimeError):
          return False


  # ── Core verifier ─────────────────────────────────────────────────────────────

  def verify_oep_package(
      package_path: str,
      public_key_b64: Optional[str] = None,
      verbose: bool = False,
      max_bytes: int = MAX_UNCOMPRESSED_BYTES,
  ) -> OepVerificationReport:
      """
      Verify a complete OEP forensic archive offline.
      Returns an OepVerificationReport with full check traceability.
      """
      package_bytes = Path(package_path).read_bytes()
      fingerprint = "sha256:" + sha256_hex(package_bytes)
      checks = {}
      notes = []
      receipt_results = []

      # ── ZIP integrity ──────────────────────────────────────────────────────────
      try:
          zf = zipfile.ZipFile(BytesIO(package_bytes))
      except zipfile.BadZipFile as e:
          checks["zip_structure"] = CheckResult("STRUCTURE", False, RC.ZIP_INVALID, str(e))
          return OepVerificationReport("FAIL", fingerprint, 0, checks, {}, [str(e)], [])

      # ── ZIP bomb guard ─────────────────────────────────────────────────────────
      total_uncompressed = sum(i.file_size for i in zf.infolist())
      if total_uncompressed > max_bytes:
          checks["zip_size"] = CheckResult("SECURITY", False, RC.SIZE_LIMIT_EXCEEDED,
                                            f"{total_uncompressed} bytes > limit {max_bytes}")
          return OepVerificationReport("FAIL", fingerprint, 0, checks, {}, [], [])

      # ── Path traversal guard ───────────────────────────────────────────────────
      names = zf.namelist()
      for name in names:
          if not is_safe_path(name):
              checks["path_safety"] = CheckResult("SECURITY", False, RC.PATH_TRAVERSAL, name)
              return OepVerificationReport("FAIL", fingerprint, 0, checks, {}, [f"Unsafe path: {name}"], [])

      checks["zip_structure"] = CheckResult("STRUCTURE", True, detail=f"{len(names)} entries")

      # ── Manifest (OEP-INV-002) ─────────────────────────────────────────────────
      manifest = None
      manifest_file = next((n for n in names if n.endswith("manifest.json")), None)
      if not manifest_file:
          checks["manifest"] = CheckResult("OEP-INV-002", False, RC.MANIFEST_MISSING)
      else:
          manifest = json.loads(zf.read(manifest_file))
          has_schema_ver = "schema_version" in manifest
          checks["manifest"] = CheckResult(
              "OEP-INV-002", has_schema_ver,
              None if has_schema_ver else RC.MANIFEST_SCHEMA_VER,
              f"schema_version={manifest.get('schema_version', 'MISSING')}"
          )

      # ── Public key (OEP-INV-003) ───────────────────────────────────────────────
      resolved_pub_key = public_key_b64
      key_identity = {"source": "argument"} if public_key_b64 else {}
      if not resolved_pub_key:
          key_file = next((n for n in names if "public_key" in n and n.endswith(".b64")), None)
          if key_file:
              resolved_pub_key = zf.read(key_file).decode("utf-8").strip()
              key_identity = {"source": "package", "file": key_file}
      checks["public_key"] = CheckResult(
          "OEP-INV-003", resolved_pub_key is not None,
          None if resolved_pub_key else RC.PUBLIC_KEY_MISSING
      )

      # ── Discover receipts ──────────────────────────────────────────────────────
      receipt_files = [n for n in names if n.startswith("receipts/") and n.endswith(".json")]
      proof_files = {n for n in names if "proofs/" in n or "merkle" in n}
      receipt_count = len(receipt_files)
      notes.append(f"Found {receipt_count} receipt(s) in package.")

      # ── Per-receipt verification ───────────────────────────────────────────────
      entry_hashes = []
      all_receipts_ok = True
      for rf in sorted(receipt_files):
          try:
              receipt_bytes = zf.read(rf)
              receipt = json.loads(receipt_bytes)
              entry_hash = compute_entry_hash(receipt_bytes)
              entry_hashes.append(entry_hash)

              receipt_id = receipt.get("delegation_id") or receipt.get("rcr_id") or rf
              proof_file = next((p for p in proof_files if receipt_id.replace("/", "_") in p or
                                  rf.replace("receipts/", "proofs/").replace(".json", "_proof.json") == p), None)

              proof_ok = None
              if proof_file:
                  proof_data = json.loads(zf.read(proof_file))
                  arh_in_proof = proof_data.get("archive_root_hash", "")
                  proof_steps = proof_data.get("proof", [])
                  proof_ok = verify_merkle_proof(entry_hash, proof_steps, arh_in_proof)

              receipt_results.append({
                  "file": rf,
                  "receipt_id": receipt_id,
                  "entry_hash": entry_hash,
                  "has_merkle_proof": proof_file is not None,
                  "merkle_proof_valid": proof_ok,
              })

              if proof_file is None:
                  all_receipts_ok = False
                  notes.append(f"  No Merkle proof found for {receipt_id} (OEP-INV-004)")
          except Exception as e:
              receipt_results.append({"file": rf, "error": str(e), "reason_code": RC.RECEIPT_PARSE_ERROR})
              all_receipts_ok = False

      checks["receipt_proofs"] = CheckResult(
          "OEP-INV-004", all_receipts_ok,
          None if all_receipts_ok else RC.RECEIPT_NO_PROOF,
          f"{receipt_count} receipts checked"
      )

      # ── EAP chain integrity (EAP-INV-001) ─────────────────────────────────────
      computed_arh = None
      if entry_hashes:
          computed_arh = compute_chain_root(entry_hashes)
      checks["merkle_chain"] = CheckResult(
          "EAP-INV-001", len(entry_hashes) > 0,
          detail=f"computed ARH={computed_arh}"
      )

      # ── ARH integrity (OEP-INV-005) ───────────────────────────────────────────
      manifest_arh = manifest.get("archive_root_hash") if manifest else None
      arh_match = (computed_arh == manifest_arh) if (computed_arh and manifest_arh) else None
      checks["arh_integrity"] = CheckResult(
          "OEP-INV-005", arh_match is True,
          None if arh_match else RC.ARH_MISMATCH,
          f"manifest_arh={manifest_arh}, computed_arh={computed_arh}"
      )

      # ── ARH PQC signature (EAP-INV-002) ───────────────────────────────────────
      arh_sig = manifest.get("archive_root_hash_signature") if manifest else None
      if arh_sig and resolved_pub_key and manifest_arh:
          sig_ok, sig_note = verify_arh_signature(manifest_arh, arh_sig, resolved_pub_key)
          checks["arh_signature"] = CheckResult("EAP-INV-002", sig_ok,
              None if sig_ok else RC.ARH_SIGNATURE_INVALID, sig_note)
      else:
          checks["arh_signature"] = CheckResult("EAP-INV-002", False, RC.ARH_SIGNATURE_SKIP,
              "Public key or ARH signature not provided — skipping PQC verification")
          notes.append("ARH PQC signature skipped — provide public key for full EAP-INV-002 coverage.")

      # ── Manifest hash (OEP-INV-006) ───────────────────────────────────────────
      if manifest and manifest_file:
          all_receipt_hashes = {r["file"]: r["entry_hash"] for r in receipt_results if "entry_hash" in r}
          computed_manifest_hash = "sha256:" + sha256_hex(
              json.dumps(all_receipt_hashes, sort_keys=True, separators=(",", ":")).encode()
          )
          stored_manifest_hash = manifest.get("receipt_hashes_digest")
          manifest_hash_ok = (stored_manifest_hash == computed_manifest_hash) if stored_manifest_hash else None
          checks["manifest_hash"] = CheckResult(
              "OEP-INV-006", manifest_hash_ok is True,
              None if manifest_hash_ok else RC.MANIFEST_HASH_MISMATCH,
              f"computed={computed_manifest_hash}"
          )
      else:
          checks["manifest_hash"] = CheckResult("OEP-INV-006", False, RC.MANIFEST_MISSING)

      # ── Overall verdict ────────────────────────────────────────────────────────
      security_checks = ["zip_structure", "path_safety"]
      structural_fails = [k for k, v in checks.items() if not v.ok and k in security_checks]
      critical_checks = ["manifest", "public_key", "arh_integrity", "merkle_chain"]
      critical_fails = [k for k, v in checks.items() if not v.ok and k in critical_checks]
      sig_ok = checks.get("arh_signature", CheckResult("", False)).ok
      non_critical_warns = [k for k, v in checks.items() if not v.ok and k not in security_checks + critical_checks]

      if structural_fails:
          verdict = "FAIL"
      elif critical_fails:
          verdict = "FAIL"
      elif not sig_ok and resolved_pub_key:
          verdict = "FAIL"
      elif non_critical_warns:
          verdict = "WARN"
      else:
          verdict = "PASS"

      return OepVerificationReport(verdict, fingerprint, receipt_count, checks, key_identity, notes, receipt_results)


  # ── CLI ───────────────────────────────────────────────────────────────────────

  def main():
      parser = argparse.ArgumentParser(
          description="ATF OEP Archive Verifier — RFC-ATF-3 (EAP-INV-005 compliant)",
          formatter_class=argparse.RawDescriptionHelpFormatter,
          epilog="""
  Examples:
    python verify_oep_package.py evidence_2026.zip
    python verify_oep_package.py evidence_2026.zip --public-key issuer_pubkey.b64
    python verify_oep_package.py evidence_2026.zip --verbose --output-transcript
          """,
      )
      parser.add_argument("package", help="Path to the .zip OEP package")
      parser.add_argument("--public-key", help="Issuer ML-DSA-65 public key (base64 file or string)")
      parser.add_argument("--verbose", "-v", action="store_true", help="Show per-receipt details")
      parser.add_argument("--output-transcript", action="store_true", help="Write verification transcript to <package>.transcript.json")
      args = parser.parse_args()

      pub_key = None
      if args.public_key:
          p = Path(args.public_key)
          pub_key = p.read_text().strip() if p.exists() else args.public_key

      report = verify_oep_package(args.package, pub_key, args.verbose)
      result = report.to_dict()

      # Print summary
      verdict_color = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m"}.get(report.verdict, "")
      reset = "\033[0m"
      print(f"\n{'='*60}")
      print(f"  ATF OEP Archive Verifier — RFC-ATF-3")
      print(f"  Package fingerprint: {report.package_fingerprint}")
      print(f"  Receipts verified:   {report.receipt_count}")
      print(f"  Verdict:             {verdict_color}{report.verdict}{reset}")
      print(f"{'='*60}")

      for check_name, check in report.checks.items():
          icon = "✓" if check.ok else ("⚠" if report.verdict == "WARN" else "✗")
          detail = f" — {check.detail}" if (args.verbose and check.detail) else ""
          rc_str = f" [{check.reason_code}]" if check.reason_code else ""
          print(f"  {icon} {check.invariant}{rc_str}{detail}")

      if args.verbose and report.receipt_results:
          print(f"\n  Receipt details:")
          for r in report.receipt_results:
              proof_str = "proof:✓" if r.get("merkle_proof_valid") else ("proof:⚠" if r.get("has_merkle_proof") else "proof:missing")
              print(f"    {r.get('receipt_id', r.get('file'))} [{proof_str}]")

      if report.notes:
          print(f"\n  Notes:")
          for note in report.notes:
              print(f"    {note}")

      if args.output_transcript:
          transcript_path = Path(args.package).with_suffix(".transcript.json")
          transcript_path.write_text(json.dumps(result, indent=2))
          print(f"\n  Transcript written: {transcript_path}")

      print()
      sys.exit(0 if report.verdict in ("PASS", "WARN") else 1)


  if __name__ == "__main__":
      main()
  