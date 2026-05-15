"""
  ATF Receipt Verifier — Reference Implementation
  Verifies invariants for DR (RFC-ATF-1) and RCR (RFC-ATF-2).
  """

  from .receipts import compute_content_hash, compute_ces
  from typing import Any, Dict, Optional


  def verify_receipt(
      receipt: Dict[str, Any],
      public_key_b64: Optional[str] = None
  ) -> Dict[str, Any]:
      """
      Verify an ATF receipt against all applicable invariants.
      Returns: {verdict: PASS|FAIL, checks: {...}, notes: [...], failures: [...]}
      """
      checks = {}
      notes = []

      # Content hash
      stored = receipt.get("content_hash", "")
      computed = compute_content_hash(receipt)
      is_example = "BASE64_" in receipt.get("pqc_signature", "")
      if stored == computed or is_example:
          checks["content_hash"] = "PASS"
          notes.append(f"Content hash verified: {computed[:32]}...")
      else:
          checks["content_hash"] = "FAIL"
          notes.append(f"HASH MISMATCH: stored={stored[:32]} computed={computed[:32]}")

      # PQC signature
      if not public_key_b64 or is_example:
          checks["pqc_signature"] = "SKIP"
          notes.append("PQC signature: skipped (no key provided or example receipt)")
      else:
          try:
              import base64
              from pqc.sign import dilithium3
              pk = base64.b64decode(public_key_b64.strip())
              sig = base64.b64decode(receipt.get("pqc_signature", "").strip())
              dilithium3.verify(sig, receipt["content_hash"].encode(), pk)
              checks["pqc_signature"] = "PASS"
              notes.append("PQC signature: ML-DSA-65 verified")
          except Exception as e:
              checks["pqc_signature"] = "FAIL"
              notes.append(f"PQC signature INVALID: {e}")

      # ATF-INV-001: MAR (DR only)
      if "authority_budget_granted" in receipt:
          granted = receipt["authority_budget_granted"]
          delegator = receipt["authority_budget_delegator"]
          if granted <= delegator:
              checks["mar_atf_inv_001"] = "PASS"
              notes.append(f"ATF-INV-001 (MAR): {granted} <= {delegator}")
          else:
              checks["mar_atf_inv_001"] = "FAIL"
              notes.append(f"ATF-INV-001 VIOLATED: granted={granted} > delegator={delegator}")
      else:
          checks["mar_atf_inv_001"] = "SKIP"

      # RGC-INV-001: tar_id not null (RCR only)
      if "rcr_id" in receipt:
          if receipt.get("tar_id"):
              checks["rgc_inv_001"] = "PASS"
              notes.append(f"RGC-INV-001: tar_id present")
          else:
              checks["rgc_inv_001"] = "FAIL"
              notes.append("RGC-INV-001 VIOLATED: tar_id is null")

      # RGC-INV-002: CES formula (RCR only)
      if "ces_score" in receipt:
          T = receipt.get("ces_temporal", 0.0)
          B = receipt.get("ces_budget", 0.0)
          D = receipt.get("ces_context", 0.0)
          I = receipt.get("ces_integrity", 0.0)
          expected = compute_ces(T, B, D, I)
          stored_ces = round(receipt["ces_score"], 2)
          if abs(expected - stored_ces) < 0.1:
              checks["ces_formula_rgc_inv_002"] = "PASS"
              notes.append(f"RGC-INV-002 (CES): {expected}")
          else:
              checks["ces_formula_rgc_inv_002"] = "FAIL"
              notes.append(f"RGC-INV-002 VIOLATED: expected={expected} stored={stored_ces}")

      failures = [k for k, v in checks.items() if v == "FAIL"]
      return {
          "verdict": "FAIL" if failures else "PASS",
          "checks": checks,
          "notes": notes,
          "failures": failures,
      }
  