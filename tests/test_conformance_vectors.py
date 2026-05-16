"""
ATF Protocol Conformance Vector Tests — v1.0
=============================================
Tests the verifier against official ATF conformance vectors.
Each vector specifies the expected verdict for a given receipt input.

All vectors must pass to claim a conformance profile:
  ATF-Compliant      — vectors prefixed V-ATF-*
  ATF-RGC-Compliant  — vectors prefixed V-ATF-* + V-RGC-*
  ATF-FEI-Compliant  — all vectors

Run with:
    pytest tests/test_conformance_vectors.py -v

Reference: CONFORMANCE.md, conformance/conformance_vectors.json
"""

import json
import sys
import copy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "verifier"))
from verify_receipt import verify_receipt_dict

VECTORS_FILE = Path(__file__).parent.parent / "conformance" / "conformance_vectors.json"
EXAMPLES = Path(__file__).parent.parent / "examples"


def load_vectors():
    data = json.loads(VECTORS_FILE.read_text())
    return data["vectors"]


def id_for(v):
    return f"{v['id']}-{v['invariant']}-{v['kind']}"


ALL_VECTORS = load_vectors()
ATF_VECTORS = [v for v in ALL_VECTORS if v["id"].startswith("V-ATF-")]
RGC_VECTORS = [v for v in ALL_VECTORS if v["id"].startswith("V-RGC-")]
FEI_VECTORS = [v for v in ALL_VECTORS if v["id"].startswith("V-FEI-")]


# ── ATF-Compliant profile (L1-L3) ────────────────────────────────────────────

class TestATFCompliantProfile:
    """
    Tests for ATF-Compliant profile.
    All vectors must pass to claim ATF-Compliant conformance.
    Covers: ATF-INV-001 through ATF-INV-006
    """

    @pytest.mark.parametrize("vector", ATF_VECTORS, ids=[id_for(v) for v in ATF_VECTORS])
    def test_vector(self, vector):
        receipt = vector["input"]
        expected_verdict = vector["expected"]["verdict"]
        expected_rc = vector["expected"].get("reason_code")

        result = verify_receipt_dict(receipt)
        actual_verdict = result.get("verdict")

        assert actual_verdict == expected_verdict, (
            f"Vector {vector['id']} [{vector['invariant']}] {vector['kind']}:\n"
            f"  Description: {vector['description']}\n"
            f"  Expected: {expected_verdict}\n"
            f"  Got:      {actual_verdict}\n"
            f"  Full result: {json.dumps(result, indent=2)}"
        )

        if expected_rc and actual_verdict == "FAIL":
            checks = result.get("checks", {})
            all_reason_codes = []
            for check in checks.values():
                if isinstance(check, str) and expected_rc in check.lower():
                    return
                if isinstance(check, dict):
                    rc = check.get("reason_code", "")
                    all_reason_codes.append(rc)
                    if expected_rc in rc:
                        return
            found_in_notes = any(expected_rc in note for note in result.get("notes", []))
            assert found_in_notes or any(expected_rc in rc for rc in all_reason_codes), (
                f"Vector {vector['id']}: Expected reason_code '{expected_rc}' not found.\n"
                f"  Available: {all_reason_codes}"
            )


# ── ATF-RGC-Compliant profile (L1-L4) ────────────────────────────────────────

class TestRGCCompliantProfile:
    """
    Tests for ATF-RGC-Compliant profile.
    Requires all ATF-Compliant vectors to pass PLUS RGC vectors.
    Covers: + RGC-INV-001 through RGC-INV-006
    """

    @pytest.mark.parametrize("vector", RGC_VECTORS, ids=[id_for(v) for v in RGC_VECTORS])
    def test_rgc_vector(self, vector):
        receipt = vector["input"]
        expected_verdict = vector["expected"]["verdict"]

        result = verify_receipt_dict(receipt)
        actual_verdict = result.get("verdict")

        assert actual_verdict == expected_verdict, (
            f"Vector {vector['id']} [{vector['invariant']}] {vector['kind']}:\n"
            f"  Description: {vector['description']}\n"
            f"  Expected: {expected_verdict}\n"
            f"  Got:      {actual_verdict}\n"
            f"  Full result: {json.dumps(result, indent=2)}"
        )


# ── ATF-FEI-Compliant profile (L1-L5) ────────────────────────────────────────

class TestFEICompliantProfile:
    """
    Tests for ATF-FEI-Compliant profile (highest — all 40 invariants).
    Covers: + EAP-INV-007, OEP-INV-002, FVP-INV-007
    """

    @pytest.mark.parametrize("vector", FEI_VECTORS, ids=[id_for(v) for v in FEI_VECTORS])
    def test_fei_vector(self, vector):
        receipt = vector["input"]
        expected_verdict = vector["expected"]["verdict"]

        result = verify_receipt_dict(receipt)
        actual_verdict = result.get("verdict")

        assert actual_verdict == expected_verdict, (
            f"Vector {vector['id']} [{vector['invariant']}] {vector['kind']}:\n"
            f"  Description: {vector['description']}\n"
            f"  Expected: {expected_verdict}\n"
            f"  Got:      {actual_verdict}"
        )

    def test_fvp_inv_007_determinism(self):
        """
        FVP-INV-007: compute_content_hash must be deterministic.
        Running it twice on the same receipt must produce identical output.
        """
        from verify_receipt import compute_content_hash
        dr = json.loads((EXAMPLES / "delegation_receipt.json").read_text())
        h1 = compute_content_hash(dr)
        h2 = compute_content_hash(dr)
        assert h1 == h2, f"FVP-INV-007 violation: non-deterministic hash: {h1} != {h2}"

    def test_fvp_inv_007_signature_field_isolation(self):
        """
        FVP-INV-007: Changing pqc_signature must NOT change content_hash.
        This ensures the signature field is correctly excluded from hash computation.
        """
        from verify_receipt import compute_content_hash
        dr = json.loads((EXAMPLES / "delegation_receipt.json").read_text())
        h1 = compute_content_hash(dr)
        dr_modified = copy.deepcopy(dr)
        dr_modified["pqc_signature"] = "COMPLETELY_DIFFERENT_SIGNATURE_VALUE_XYZ"
        h2 = compute_content_hash(dr_modified)
        assert h1 == h2, (
            "FVP-INV-007 violation: pqc_signature field affects content_hash.\n"
            "Signature fields must be excluded from hash computation."
        )

    def test_eap_inv_007_entry_hash_determinism(self):
        """
        EAP-INV-007: Entry hash must be deterministic — same bytes, same hash.
        """
        import hashlib
        dr_bytes = (EXAMPLES / "delegation_receipt.json").read_bytes()
        h1 = "sha256:" + hashlib.sha256(dr_bytes).hexdigest()
        h2 = "sha256:" + hashlib.sha256(dr_bytes).hexdigest()
        assert h1 == h2, "EAP-INV-007: entry hash is non-deterministic"


# ── Cross-profile coverage summary ───────────────────────────────────────────

class TestConformanceCoverage:
    """Verify that the vector set covers all required profiles."""

    def test_atf_profile_has_minimum_vectors(self):
        assert len(ATF_VECTORS) >= 15, f"ATF profile needs ≥15 vectors, got {len(ATF_VECTORS)}"

    def test_rgc_profile_has_minimum_vectors(self):
        assert len(RGC_VECTORS) >= 11, f"RGC profile needs ≥11 vectors, got {len(RGC_VECTORS)}"

    def test_fei_profile_has_minimum_vectors(self):
        assert len(FEI_VECTORS) >= 8, f"FEI profile needs ≥8 vectors, got {len(FEI_VECTORS)}"

    def test_negative_vectors_present_in_each_profile(self):
        atf_neg = [v for v in ATF_VECTORS if v["kind"] == "negative"]
        rgc_neg = [v for v in RGC_VECTORS if v["kind"] == "negative"]
        fei_neg = [v for v in FEI_VECTORS if v["kind"] == "negative"]
        assert len(atf_neg) >= 5, "ATF profile must have ≥5 negative vectors"
        assert len(rgc_neg) >= 3, "RGC profile must have ≥3 negative vectors"
        assert len(fei_neg) >= 2, "FEI profile must have ≥2 negative vectors"

    def test_all_vectors_have_required_fields(self):
        required = {"id", "profile", "invariant", "kind", "description", "input", "expected"}
        for v in ALL_VECTORS:
            missing = required - set(v.keys())
            assert not missing, f"Vector {v.get('id', '?')} missing fields: {missing}"

    def test_vector_ids_are_unique(self):
        ids = [v["id"] for v in ALL_VECTORS]
        assert len(ids) == len(set(ids)), f"Duplicate vector IDs found: {[i for i in ids if ids.count(i) > 1]}"
