# Contributing to ATF Protocol Standard

  Thank you for your interest in the Agent Trust Fabric (ATF) protocol.
  This is a technical standards repository — contributions are held to the same
  standard as protocol invariants: precise, traceable, and proof-backed.

  ---

  ## Contribution Ladder

  | Level | What you contribute | How to start |
  |---|---|---|
  | **L0** | Bug report, ambiguity, typo | Open a GitHub Issue |
  | **L1** | Conformance test vector | PR to `tests/` |
  | **L2** | Language port | See Port Guide below |
  | **L3** | New invariant proposal | RFC Process (see GOVERNANCE.md §3) |
  | **L4** | New RFC draft | Discuss in Issues first |

  ---

  ## Reporting Issues

  Open a GitHub Issue for:
  - Ambiguities or inconsistencies in the RFC text
  - Gaps in invariant coverage
  - Proposed new invariant families
  - Errors in examples or schemas
  - Security vulnerabilities (use GitHub Security Advisories for private disclosure)

  ---

  ## Pull Requests

  ### Conformance Test Vectors

  Add test cases to `tests/test_atf_receipts.py` or `tests/test_conformance_vectors.py`.

  Every test must:
  1. Reference the specific invariant (e.g., `# ATF-INV-001`)
  2. Include both a positive (PASS) and negative (FAIL) vector for each new case
  3. Use the normative reason code in FAIL assertions

  Example structure:
  ```python
  # ATF-INV-001: MAR boundary condition
  def test_budget_at_exact_delegator_limit():
      receipt = make_dr({"authority_budget_granted": 100.0, "authority_budget_delegator": 100.0})
      ok, _ = check_mar_invariant(receipt)
      assert ok is True   # granted == delegator is valid

  def test_budget_one_cent_over_delegator():
      receipt = make_dr({"authority_budget_granted": 100.01, "authority_budget_delegator": 100.0})
      ok, _ = check_mar_invariant(receipt)
      assert ok is False  # ATF-INV-001 violation
  ```

  ### Threat Model Tests

  New adversarial inputs belong in `tests/test_threat_model.py` with a corresponding
  entry in `THREAT_MODEL.md §7 (Remediation Tracker)`.

  ### Reference Implementation

  Contributions to `reference-implementation/`:
  - Bug fixes in invariant verification logic must include a negative conformance test
  - New helpers must be language-agnostic (no platform assumptions)
  - Invariant enforcement at creation time (fail-fast) is preferred over silent fallbacks

  ---

  ## Language Ports

  ### Quick start: Rust (implementation needed)

  The fastest path to a complete external implementation — all scaffolding is done:

  ```bash
  git clone https://github.com/Costenho19/atf-protocol-standard
  cd atf-protocol-standard/ports/rust
  cargo test   # See which tests fail — expected output: "not implemented"
  ```

  Implement three functions in `src/lib.rs`:
  1. `compute_content_hash()` — canonical JSON + SHA-256
  2. `verify_delegation_receipt()` — ATF-INV-001–006
  3. `verify_runtime_continuity_record()` — RGC-INV-001–004

  Make `cargo test` pass all 34 vectors. Open a PR.
  See [`ports/rust/PORTING_GUIDE.md`](./ports/rust/PORTING_GUIDE.md) for the
  complete 14-step guide with Python reference pseudocode.

  ### New language port (Go, Java, Swift, etc.)

  Port requirements:
  1. **Implement all 14 invariants** from RFC-ATF-1 + RFC-ATF-2 (`ATF-RGC-Compliant`)
  2. **Pass JSON interoperability** — verify receipts produced by the Python reference
  3. **Canonical JSON parity** — `compute_content_hash()` must produce byte-identical
     output to Python for all 34 conformance vectors (FVP-INV-007)
  4. **Normative reason codes** — FAIL results must use the reason codes from
     `conformance/conformance_vectors.json`
  5. **README** with build, test, and compliance claim instructions

  Canonical JSON rules (critical for cross-language parity):
  - Keys sorted lexicographically (recursive)
  - Compact separators: `","` and `":"`
  - No spaces, no trailing commas
  - `UTF-8` encoding
  - Excluded fields: `content_hash`, `pqc_signature`, `pqc_algorithm`, `_comment`, `_ces_formula`

  Edge cases to handle:
  - `execution_ns` values > 2⁵³ — use 64-bit integers, not floats
  - Whole-number floats: `90.0` — Python serializes as `"90.0"`; TypeScript/Rust
    normalize to `90`. Pick one convention and document it in your README.

  ### Schema Extensions

  Propose new JSON Schemas via Issue first, then submit a PR with:
  - The schema file in `schemas/`
  - At least one example in `examples/`
  - A corresponding conformance test in `tests/`
  - An update to `COMPLIANCE-MATRIX.md`

  ---

  ## Security Contributions

  Found a vulnerability in the verifier or reference implementation?

  1. **Private disclosure first** — use GitHub Security Advisories, not a public PR.
  2. Include: affected component, reproduction steps, severity assessment, proposed fix.
  3. The Editor will acknowledge within 24 hours for Critical/High issues.
  4. Once fixed, you will be credited in `CHANGELOG.md` and `THREAT_MODEL.md §9`.

  See [SECURITY.md](./SECURITY.md) and [THREAT_MODEL.md](./THREAT_MODEL.md) for the
  full security policy and current attack surface documentation.

  ---

  ## Code of Conduct

  This is a technical standards repository. Contributions must be:
  - **Technically precise** — vague language weakens invariants
  - **Protocol-neutral** — no vendor-specific assumptions
  - **Traceable** — every design decision references the relevant RFC section
  - **Tested** — every invariant claim must have a conformance test

  ---

  ## Governance

  The ATF protocol is maintained by **OMNIX QUANTUM LTD**.
  Significant changes to invariants require a new RFC revision.
  Bug fixes and clarifications are applied as errata without a new RFC.
  See [GOVERNANCE.md](./GOVERNANCE.md) for the full process.

  Contact: standards@omnixquantum.com

  ---

  *OMNIX QUANTUM LTD · CC BY 4.0*
  