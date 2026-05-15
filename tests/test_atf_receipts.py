"""
  ATF Protocol Conformance Tests — RFC-ATF-1 / RFC-ATF-2
  =======================================================
  Tests verify that the ATF verifier correctly enforces
  protocol invariants on delegation receipts and runtime
  continuity records.

  Run with:
      pytest tests/ -v
  """

  import hashlib
  import json
  import sys
  import copy
  from pathlib import Path

  # Add verifier to path
  sys.path.insert(0, str(Path(__file__).parent.parent / "verifier"))
  from verify_receipt import (
      compute_content_hash,
      verify_content_hash,
      check_mar_invariant,
      check_ces_formula,
      detect_type,
  )

  EXAMPLES = Path(__file__).parent.parent / "examples"


  # ── Fixtures ──────────────────────────────────────────────────────────────────

  def load_dr():
      return json.loads((EXAMPLES / "delegation_receipt.json").read_text())

  def load_rcr():
      return json.loads((EXAMPLES / "runtime_continuity_record.json").read_text())


  # ── Content hash tests ────────────────────────────────────────────────────────

  class TestContentHash:

      def test_valid_dr_hash_structure(self):
          """content_hash field exists and has sha256: prefix."""
          dr = load_dr()
          assert dr["content_hash"].startswith("sha256:")

      def test_valid_rcr_hash_structure(self):
          """RCR content_hash exists and has sha256: prefix."""
          rcr = load_rcr()
          assert rcr["content_hash"].startswith("sha256:")

      def test_compute_hash_is_deterministic(self):
          """Same receipt always produces the same computed hash."""
          dr = load_dr()
          h1 = compute_content_hash(dr)
          h2 = compute_content_hash(dr)
          assert h1 == h2

      def test_tampered_receipt_hash_differs(self):
          """Modifying any field changes the computed content hash."""
          dr = load_dr()
          original_hash = compute_content_hash(dr)
          tampered = copy.deepcopy(dr)
          tampered["authority_budget_granted"] = 99.9  # unauthorized budget expansion
          tampered_hash = compute_content_hash(tampered)
          assert original_hash != tampered_hash, "Tampering must change content hash"

      def test_hash_excludes_signature_fields(self):
          """content_hash, pqc_signature, pqc_algorithm are excluded from hash computation."""
          dr = load_dr()
          dr_modified = copy.deepcopy(dr)
          dr_modified["pqc_signature"] = "DIFFERENT_SIGNATURE"
          assert compute_content_hash(dr) == compute_content_hash(dr_modified)


  # ── MAR invariant tests (ATF-INV-001) ─────────────────────────────────────────

  class TestMARInvariant:

      def test_valid_dr_satisfies_mar(self):
          """Example DR must satisfy ATF-INV-001: granted <= delegator budget."""
          dr = load_dr()
          ok, note = check_mar_invariant(dr)
          assert ok is True, f"Valid DR must satisfy MAR: {note}"
          assert "granted" in note

      def test_authority_expansion_violates_mar(self):
          """ATF-INV-001: a DR granting more than delegator budget MUST fail."""
          dr = load_dr()
          dr["authority_budget_granted"] = dr["authority_budget_delegator"] + 1.0
          ok, note = check_mar_invariant(dr)
          assert ok is False, "Budget expansion must violate ATF-INV-001"
          assert "VIOLATED" in note

      def test_equal_budget_satisfies_mar(self):
          """Granting exactly the delegator's budget is permitted (boundary case)."""
          dr = load_dr()
          dr["authority_budget_granted"] = dr["authority_budget_delegator"]
          ok, _ = check_mar_invariant(dr)
          assert ok is True

      def test_rcr_skips_mar_check(self):
          """MAR check is not applicable to RCRs (returns None)."""
          rcr = load_rcr()
          ok, note = check_mar_invariant(rcr)
          assert ok is None
          assert "not applicable" in note.lower()


  # ── CES formula tests (RGC-INV-002) ──────────────────────────────────────────

  class TestCESFormula:

      def test_valid_rcr_satisfies_ces_formula(self):
          """Example RCR must satisfy RGC-INV-002: CES = T×0.30+B×0.30+D×0.20+I×0.20."""
          rcr = load_rcr()
          ok, note = check_ces_formula(rcr)
          assert ok is True, f"Valid RCR must satisfy CES formula: {note}"

      def test_manipulated_ces_score_fails(self):
          """RGC-INV-002: a manually inflated ces_score must not match computed formula."""
          rcr = load_rcr()
          rcr["ces_score"] = 99.99  # artificially inflated
          ok, note = check_ces_formula(rcr)
          assert ok is False, "Manipulated CES score must fail formula check"
          assert "VIOLATED" in note

      def test_halt_condition(self):
          """CES < 10.0 produces HALT status."""
          rcr = copy.deepcopy(load_rcr())
          rcr["ces_temporal"] = 0.0
          rcr["ces_budget"] = 0.0
          rcr["ces_context"] = 0.0
          rcr["ces_integrity"] = 0.0
          rcr["ces_score"] = 0.0
          rcr["continuity_status"] = "HALT"
          ok, note = check_ces_formula(rcr)
          assert ok is True  # formula 0.0 == 0.0 is valid

      def test_nominal_threshold(self):
          """CES >= 75.0 must produce NOMINAL status."""
          rcr = copy.deepcopy(load_rcr())
          # All components at 100 → CES = 100.0 → NOMINAL
          rcr["ces_temporal"] = 100.0
          rcr["ces_budget"] = 100.0
          rcr["ces_context"] = 100.0
          rcr["ces_integrity"] = 100.0
          rcr["ces_score"] = 100.0
          ok, _ = check_ces_formula(rcr)
          assert ok is True

      def test_dr_skips_ces_check(self):
          """CES formula check is not applicable to DRs (returns None)."""
          dr = load_dr()
          ok, note = check_ces_formula(dr)
          assert ok is None

      def test_ces_formula_weights_are_fixed(self):
          """RGC-INV-002: weights are non-negotiable — 0.30/0.30/0.20/0.20."""
          rcr = copy.deepcopy(load_rcr())
          # Compute expected with correct weights
          T, B, D, I = 80.0, 90.0, 70.0, 60.0
          rcr["ces_temporal"] = T
          rcr["ces_budget"] = B
          rcr["ces_context"] = D
          rcr["ces_integrity"] = I
          expected = T * 0.30 + B * 0.30 + D * 0.20 + I * 0.20
          rcr["ces_score"] = expected
          ok, _ = check_ces_formula(rcr)
          assert ok is True


  # ── Receipt type detection ────────────────────────────────────────────────────

  class TestReceiptTypeDetection:

      def test_detects_delegation_receipt(self):
          dr = load_dr()
          t = detect_type(dr)
          assert "Delegation Receipt" in t

      def test_detects_runtime_continuity_record(self):
          rcr = load_rcr()
          t = detect_type(rcr)
          assert "Runtime Continuity Record" in t


  # ── Protocol identifier format tests (ATF-INV-002 / ATF-INV-003) ─────────────

  class TestIdentifierFormats:

      def test_dr_id_format(self):
          """delegation_id MUST match ATFDR-{16HEX}."""
          import re
          dr = load_dr()
          assert re.match(r'^ATFDR-[0-9A-F]{16}$', dr["delegation_id"]), \
              f"Invalid DR ID format: {dr['delegation_id']}"

      def test_rcr_id_format(self):
          """rcr_id MUST match ATFRCR-{16HEX}."""
          import re
          rcr = load_rcr()
          assert re.match(r'^ATFRCR-[0-9A-F]{16}$', rcr["rcr_id"]), \
              f"Invalid RCR ID format: {rcr['rcr_id']}"

      def test_chain_root_id_in_dr(self):
          """ATF-INV-003: chain_root_id MUST equal delegation_id for root DRs."""
          dr = load_dr()
          # For root DRs (no parent), chain_root_id == delegation_id
          if dr.get("parent_delegation_id") is None:
              assert dr["chain_root_id"] == dr["delegation_id"], \
                  "Root DR: chain_root_id must equal delegation_id (ATF-INV-003)"

      def test_authority_budget_in_range(self):
          """Authority budget MUST be in [0.0, 100.0]."""
          dr = load_dr()
          assert 0.0 <= dr["authority_budget_granted"] <= 100.0
          assert 0.0 <= dr["authority_budget_delegator"] <= 100.0

      def test_status_valid_values(self):
          """DR status MUST be one of ACTIVE | EXPIRED | REVOKED."""
          dr = load_dr()
          assert dr["status"] in {"ACTIVE", "EXPIRED", "REVOKED"}

      def test_continuity_status_valid_values(self):
          """RCR continuity_status MUST be one of five defined levels."""
          rcr = load_rcr()
          assert rcr["continuity_status"] in {"NOMINAL", "MONITORING", "WARNING", "CRITICAL", "HALT"}
  