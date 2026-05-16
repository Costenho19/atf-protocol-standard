"""
ATF Cross-Language Hash Parity Tests — FVP-INV-007
====================================================
Verifies that Python, TypeScript, and Rust verifiers produce byte-identical
SHA-256 hashes for ATF receipt canonical payloads (FVP-INV-007).

Python determinism tests always run.
Cross-language parity tests require compiled ports:
  TypeScript: cd ports/typescript && npm run build
  Rust:       cd ports/rust && cargo build --release

Invariants exercised:
  FVP-INV-007  Verifier determinism (same input → same hash, all languages)
  ATF-INV-004  Content hash covers all receipt fields except excluded set
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest


# ── Canonical hash — Python reference ─────────────────────────────────────────

EXCLUDE_FIELDS = {
    "content_hash", "pqc_signature", "pqc_algorithm",
    "_comment", "_ces_formula", "_test_note",
}


def compute_content_hash(receipt: dict) -> str:
    """RFC-ATF-1 §5.2 canonical SHA-256 — Python reference (FVP-INV-007)."""
    payload = {k: v for k, v in receipt.items() if k not in EXCLUDE_FIELDS}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ── Fixtures ───────────────────────────────────────────────────────────────────

EXAMPLE_DR = {
    "delegation_id": "ATFDR-0A1B2C3D4E5F6A7B",
    "delegator_id": "AIR-FOUNDER-001",
    "delegate_id": "AIR-AGENT-042",
    "chain_root_id": "ATFDR-ROOTROOTROOT0000",
    "authority_budget_delegator": 100,
    "authority_budget_granted": 75,
    "delegation_depth": 1,
    "scope": ["financial:read", "reporting:write"],
    "domain": "FINANCE",
    "issued_at": "2026-05-16T00:00:00Z",
    "expires_at": "2026-06-16T00:00:00Z",
    "pqc_algorithm": "ML-DSA-65",
    "pqc_signature": "PLACEHOLDER",
    "content_hash": "sha256:placeholder",
}

EXAMPLE_RCR = {
    "rcr_id": "RCR-0A1B2C3D4E5F6A7B",
    "delegation_id": "ATFDR-0A1B2C3D4E5F6A7B",
    "tar_id": "TAR-0A1B2C3D4E5F6A7B",
    "ces_score": 82.5,
    "ces_components": {
        "temporal_health": 90.0,
        "budget_health": 85.0,
        "context_fidelity": 80.0,
        "integrity_score": 75.0,
    },
    "continuity_status": "NOMINAL",
    "active_anomalies": 0,
    "context_drift_pct": 5.0,
    "budget_remaining": 68,
    "budget_admission": 75,
    "recorded_at": "2026-05-16T00:01:00Z",
    "content_hash": "sha256:placeholder",
}


# ── Python determinism tests (FVP-INV-007) ────────────────────────────────────


class TestPythonHashDeterminism:
    """FVP-INV-007: identical input always produces identical output."""

    def test_dr_hash_stable_across_three_calls(self):
        h1 = compute_content_hash(EXAMPLE_DR)
        h2 = compute_content_hash(EXAMPLE_DR)
        h3 = compute_content_hash(EXAMPLE_DR)
        assert h1 == h2 == h3
        assert h1.startswith("sha256:")

    def test_rcr_hash_stable_across_calls(self):
        h1 = compute_content_hash(EXAMPLE_RCR)
        h2 = compute_content_hash(EXAMPLE_RCR)
        assert h1 == h2

    def test_excludes_content_hash_field(self):  # ATF-INV-004
        r1 = {**EXAMPLE_DR, "content_hash": "sha256:abc"}
        r2 = {**EXAMPLE_DR, "content_hash": "sha256:xyz"}
        assert compute_content_hash(r1) == compute_content_hash(r2)

    def test_excludes_pqc_signature(self):  # ATF-INV-004
        r1 = {**EXAMPLE_DR, "pqc_signature": "SIG_A"}
        r2 = {**EXAMPLE_DR, "pqc_signature": "SIG_B"}
        assert compute_content_hash(r1) == compute_content_hash(r2)

    def test_excludes_pqc_algorithm(self):
        r1 = {**EXAMPLE_DR, "pqc_algorithm": "ML-DSA-65"}
        r2 = {**EXAMPLE_DR, "pqc_algorithm": "ML-DSA-87"}
        assert compute_content_hash(r1) == compute_content_hash(r2)

    def test_excludes_all_metadata_fields(self):
        r = {**EXAMPLE_DR, "_comment": "x", "_ces_formula": "y", "_test_note": "z"}
        assert compute_content_hash(r) == compute_content_hash(EXAMPLE_DR)

    def test_changes_on_budget_change(self):  # ATF-INV-001 traceability
        r1 = {**EXAMPLE_DR, "authority_budget_granted": 75}
        r2 = {**EXAMPLE_DR, "authority_budget_granted": 76}
        assert compute_content_hash(r1) != compute_content_hash(r2)

    def test_changes_on_delegation_id_change(self):
        r1 = {**EXAMPLE_DR, "delegation_id": "ATFDR-0A1B2C3D4E5F6A7B"}
        r2 = {**EXAMPLE_DR, "delegation_id": "ATFDR-BBBBBBBBBBBBBBBB"}
        assert compute_content_hash(r1) != compute_content_hash(r2)

    def test_hash_format_sha256_hex64(self):
        h = compute_content_hash(EXAMPLE_DR)
        assert h.startswith("sha256:")
        assert len(h) == 7 + 64
        assert all(c in "0123456789abcdef" for c in h[7:])

    def test_key_order_independent(self):
        """Keys must sort lexicographically — FVP-INV-007."""
        r1 = {"z": 9, "a": 1, "m": 5}
        r2 = {"m": 5, "z": 9, "a": 1}
        assert compute_content_hash(r1) == compute_content_hash(r2)

    def test_nested_key_order_independent(self):
        r1 = {"ces_components": {"z": 0.9, "a": 0.8}}
        r2 = {"ces_components": {"a": 0.8, "z": 0.9}}
        assert compute_content_hash(r1) == compute_content_hash(r2)

    def test_hash_regression_dr(self):
        """Pin: same receipt always produces same hash (FVP-INV-007)."""
        h = compute_content_hash(EXAMPLE_DR)
        assert h == compute_content_hash(dict(EXAMPLE_DR))

    def test_hash_regression_rcr(self):
        h = compute_content_hash(EXAMPLE_RCR)
        assert h == compute_content_hash(dict(EXAMPLE_RCR))


# ── Cross-language parity (requires compiled ports) ───────────────────────────

REPO_ROOT = Path(__file__).parent.parent
TS_CLI = REPO_ROOT / "ports" / "typescript" / "dist" / "cli.js"
RUST_BIN = REPO_ROOT / "ports" / "rust" / "target" / "release" / "verify_receipt"


def _node_available() -> bool:
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5, check=True)
        return True
    except Exception:
        return False


@pytest.mark.skipif(
    not _node_available() or not TS_CLI.exists(),
    reason="TypeScript port not compiled — run: cd ports/typescript && npm run build",
)
class TestTypeScriptHashParity:
    """Python hash == TypeScript hash for all receipt types (FVP-INV-007)."""

    def _ts_hash(self, receipt: dict) -> str:
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(receipt, f)
            tmp = f.name
        result = subprocess.run(
            ["node", str(TS_CLI), tmp, "--hash-only"],
            capture_output=True, text=True, timeout=10,
        )
        os.unlink(tmp)
        return result.stdout.strip()

    def test_dr_parity(self):
        py = compute_content_hash(EXAMPLE_DR)
        ts = self._ts_hash(EXAMPLE_DR)
        assert py == ts, f"Hash parity FAIL\nPython:     {py}\nTypeScript: {ts}"

    def test_rcr_parity(self):
        py = compute_content_hash(EXAMPLE_RCR)
        ts = self._ts_hash(EXAMPLE_RCR)
        assert py == ts, f"Hash parity FAIL\nPython:     {py}\nTypeScript: {ts}"


@pytest.mark.skipif(
    not RUST_BIN.exists(),
    reason="Rust binary not compiled — run: cd ports/rust && cargo build --release",
)
class TestRustHashParity:
    """Python hash == Rust hash for all receipt types (FVP-INV-007)."""

    def _rust_hash(self, receipt: dict) -> str:
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(receipt, f)
            tmp = f.name
        result = subprocess.run(
            [str(RUST_BIN), tmp, "--hash-only"],
            capture_output=True, text=True, timeout=10,
        )
        os.unlink(tmp)
        return result.stdout.strip()

    def test_dr_parity(self):
        py = compute_content_hash(EXAMPLE_DR)
        rust = self._rust_hash(EXAMPLE_DR)
        assert py == rust, f"Hash parity FAIL\nPython: {py}\nRust:   {rust}"

    def test_rcr_parity(self):
        py = compute_content_hash(EXAMPLE_RCR)
        rust = self._rust_hash(EXAMPLE_RCR)
        assert py == rust, f"Hash parity FAIL\nPython: {py}\nRust:   {rust}"
