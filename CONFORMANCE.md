# ATF Conformance Program — v1.0

  The ATF Conformance Program is the official mechanism by which implementations
  of the Agent Trust Fabric protocol declare and evidence their compliance.

  **Three profiles — progressively stricter:**

  | Profile | RFC Coverage | Invariants | Use Case |
  |---|---|---|---|
  | `ATF-Compliant` | RFC-ATF-1 | 6 (ATF-INV-001–006) | Basic AI agent delegation |
  | `ATF-RGC-Compliant` | RFC-ATF-1 + RFC-ATF-2 | 14 | Long-running agent tasks |
  | `ATF-FEI-Compliant` | RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3 | 40 | Forensic / regulatory grade |

  ---

  ## How to Claim Conformance

  ### Step 1 — Run the official test vectors

  ```bash
  pip install pytest pypqc jsonschema
  pytest tests/test_conformance_vectors.py -v --tb=short
  ```

  All vectors for the target profile must produce the expected verdict.

  ### Step 2 — Run the offline verifier

  ```bash
  python verifier/verify_receipt.py examples/delegation_receipt.json
  python verifier/verify_receipt.py examples/runtime_continuity_record.json
  ```

  Both must return `PASS`.

  ### Step 3 — For `ATF-FEI-Compliant`: verify an OEP package

  ```bash
  python verifier/verify_oep_package.py <your_evidence.zip> --public-key <issuer_pub.b64>
  ```

  Must return `PASS`.

  ### Step 4 — Produce your Implementation Report

  Your report must include:

  ```json
  {
    "implementation": "<name>",
    "version": "<version>",
    "profile": "ATF-Compliant | ATF-RGC-Compliant | ATF-FEI-Compliant",
    "language": "<language>",
    "pqc_library": "<library and version>",
    "invariants_covered": ["ATF-INV-001", "..."],
    "test_vector_run": {
      "total": <n>,
      "passed": <n>,
      "failed": 0,
      "ci_url": "<url>"
    },
    "verified_by": "<name or org>",
    "date": "YYYY-MM-DD"
  }
  ```

  ### Step 5 — Register in IMPLEMENTATIONS.md

  Open a Pull Request adding your implementation to
  [IMPLEMENTATIONS.md](./IMPLEMENTATIONS.md) with your report linked.

  ---

  ## Badge Usage

  After completing the above steps, you may use the appropriate badge in your
  repository:

  ```markdown
  ![ATF-Compliant](https://img.shields.io/badge/ATF--Compliant-RFC--ATF--1-blue?style=flat-square)
  ![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-RFC--ATF--2-blue?style=flat-square)
  ![ATF-FEI-Compliant](https://img.shields.io/badge/ATF--FEI--Compliant-RFC--ATF--3-blue?style=flat-square)
  ```

  Badges must link to your Implementation Report or CI run. Unverified badge usage
  is a protocol violation.

  ---

  ## Conformance Test Vectors

  Vectors are defined in [`conformance/conformance_vectors.json`](./conformance/conformance_vectors.json).

  Each vector specifies:

  | Field | Description |
  |---|---|
  | `id` | Unique vector ID (e.g. `V-ATF-001-P`) |
  | `profile` | Target conformance profile |
  | `invariant` | Invariant under test |
  | `kind` | `positive` (must PASS) or `negative` (must FAIL) |
  | `description` | Human-readable test description |
  | `input` | Receipt JSON or partial receipt |
  | `expected.verdict` | `PASS` or `FAIL` |
  | `expected.reason_code` | Normative reason code for FAIL cases |

  **Test vector counts by profile:**

  | Profile | Positive | Negative | Total |
  |---|---|---|---|
  | ATF-Compliant (L1–L3) | 8 | 7 | 15 |
  | ATF-RGC-Compliant (L1–L4) | 6 | 5 | 11 |
  | ATF-FEI-Compliant (L1–L5) | 4 | 4 | 8 |
  | **Total** | **18** | **16** | **34** |

  ---

  ## Invariant-to-Vector Mapping

  | Invariant | Vector IDs (positive) | Vector IDs (negative) |
  |---|---|---|
  | ATF-INV-001 (MAR) | V-ATF-001-P, V-ATF-002-P, V-ATF-003-P | V-ATF-001-N, V-ATF-002-N |
  | ATF-INV-002 (ID format) | V-ATF-004-P | V-ATF-003-N |
  | ATF-INV-003 (chain root) | V-ATF-005-P | V-ATF-004-N |
  | ATF-INV-004 (sig coverage) | V-ATF-006-P | V-ATF-005-N |
  | ATF-INV-005 (offline) | V-ATF-007-P | — |
  | ATF-INV-006 (temporal) | V-ATF-008-P | V-ATF-006-N, V-ATF-007-N |
  | RGC-INV-001 (tar_id) | V-RGC-001-P | V-RGC-001-N |
  | RGC-INV-002 (CES formula) | V-RGC-002-P, V-RGC-003-P | V-RGC-002-N, V-RGC-003-N |
  | RGC-INV-003 (status) | V-RGC-004-P | V-RGC-004-N |
  | RGC-INV-004 (HALT propagate) | V-RGC-005-P | V-RGC-005-N |
  | RGC-INV-006 (execution_ns) | V-RGC-006-P | — |
  | EAP-INV-005 (offline) | V-FEI-001-P | — |
  | EAP-INV-007 (entry hash) | V-FEI-002-P | V-FEI-001-N |
  | OEP-INV-002 (manifest) | V-FEI-003-P | V-FEI-002-N |
  | FVP-INV-007 (determinism) | V-FEI-004-P | V-FEI-003-N, V-FEI-004-N |

  ---

  ## Determinism Requirement (FVP-INV-007)

  Any two conformant verifier implementations, given identical input (same receipt
  JSON and same public key), MUST produce identical output: same verdict, same
  check results, same reason codes.

  This is a hard requirement. Non-deterministic implementations cannot claim
  any ATF conformance profile.

  ---

  ## Errata and Vector Updates

  Conformance vectors are versioned alongside the protocol. A vector update that
  changes expected verdicts constitutes a minor version bump. Vector additions are
  patch-level changes.

  Current version: **v1.0** (released with RFC-ATF-3, May 2026)

  ---

  *OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
  