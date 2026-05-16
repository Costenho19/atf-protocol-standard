# ATF Protocol Standard — Governance Model

  **Version:** 1.0 · **Effective:** May 2026 · **Editor:** Harold Nunes, OMNIX QUANTUM LTD

  This document defines the governance model for the Agent Trust Fabric (ATF)
  Protocol Standard. It establishes how the specification evolves, how decisions
  are made, and how the community participates.

  ---

  ## 1. Principles

  **Stability first.** Protocol invariants (ATF-INV-001 through FVP-INV-007) are
  immutable after ratification. Implementations that pass the conformance suite
  today will continue to pass it indefinitely.

  **Proof-backed changes.** Every new invariant or protocol change must be accompanied
  by formal specification and at least one conformance test vector. Opinion-only
  changes are not accepted.

  **Independent verifiability.** ATF-INV-006 is also a governance principle:
  no governance decision may make the protocol less independently verifiable.

  **Language agnosticism.** The reference implementation (Python) is the source of
  truth for ambiguous cases. All language ports must produce identical output for
  identical input.

  ---

  ## 2. RFC Process

  ATF is specified through a series of RFCs. Each RFC follows this lifecycle:

  ```
  DRAFT → REVIEW → CANDIDATE → RATIFIED → PUBLISHED
  ```

  | Stage | Description |
  |---|---|
  | **DRAFT** | Work in progress. Breaking changes allowed. |
  | **REVIEW** | Feature-complete. External review period: 30 days. |
  | **CANDIDATE** | Changes frozen. Conformance suite finalized. |
  | **RATIFIED** | Approved by Editor. Invariants are now stable. |
  | **PUBLISHED** | DOI assigned. Citable. Implementations may claim compliance. |

  ### Published RFCs

  | RFC | Title | Status | DOI / SSRN |
  |---|---|---|---|
  | RFC-ATF-1 | Agent Trust Fabric Delegation Protocol | **PUBLISHED** | [DOI: 10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016) · [SSRN: 6757339](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339) |
  | RFC-ATF-2 | Runtime Governance Continuity Protocol | **PUBLISHED** | [SSRN: 6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978) |
  | RFC-ATF-3 | Evidence Lifecycle, Policy Interoperability & Forensic Verification | **CANDIDATE** | Zenodo pending |

  ### Proposing a new RFC

  1. Open a GitHub Issue with title `[RFC] <short title>`.
  2. Include: motivation, invariants proposed, failure mode addressed.
  3. After discussion, the Editor opens an RFC document in `/rfcs/`.
  4. 30-day review period. Substantive objections must include a test vector.
  5. Editor ratifies or closes with explanation.

  ---

  ## 3. Versioning Policy

  ATF follows **semantic versioning** with protocol-specific semantics:

  | Change | Version bump | Example |
  |---|---|---|
  | New invariant (breaking) | **MAJOR** | 1.x → 2.0 |
  | New non-normative guidance | **MINOR** | 1.0 → 1.1 |
  | Clarification, typo, example fix | **PATCH** | 1.0.0 → 1.0.1 |

  **Invariant stability guarantee:** Once ratified, an invariant's reason code
  and check logic are never modified. Existing conformance vectors are never
  invalidated. New vectors may be added; existing ones are immutable.

  **Version compatibility:** Implementations claiming `ATF-Compliant v1.x` must
  pass all vectors from v1.0.0 onward. No vector is ever removed.

  ---

  ## 4. Conformance Claims

  Conformance is self-claimed based on the conformance test suite.
  Three profiles exist:

  | Profile | Invariants | Test vectors required |
  |---|---|---|
  | **ATF-Compliant** | ATF-INV-001–006 | 15 (8 positive + 7 negative) |
  | **ATF-RGC-Compliant** | + RGC-INV-001–008 | + 11 (6P + 5N) |
  | **ATF-FEI-Compliant** | + GPIL + EAP + OEP + FEA + FVP | + 8 (4P + 4N) |

  To claim a profile:
  1. Run the conformance suite against your implementation.
  2. Open a PR adding your implementation to `IMPLEMENTATIONS.md`.
  3. The Editor reviews and merges.

  **The Editor does not certify implementations.** Conformance claims are the
  responsibility of the implementation authors. False claims may be removed
  from IMPLEMENTATIONS.md.

  ---

  ## 5. Implementation Registry

  See `IMPLEMENTATIONS.md` for the list of known ATF-compliant implementations.
  The registry is informational — not exhaustive.

  To add your implementation:
  ```markdown
  | [Your Project](https://link) | Language | Profile | Version | Maintainer |
  ```

  ---

  ## 6. Security Policy

  See `SECURITY.md` for the full security policy.

  Summary:
  - Report vulnerabilities privately via GitHub Security Advisories.
  - The Editor will acknowledge within 72 hours.
  - Protocol-level vulnerabilities (invariant bypass) are treated as critical.
  - Implementation bugs in the reference implementation follow the same process.

  ---

  ## 7. Deprecation Policy

  ATF does not deprecate ratified invariants. Once an invariant is published,
  it remains in the specification permanently (for backward compatibility).

  Deprecation may occur for:
  - Non-normative guidance (replaced by clearer guidance)
  - Example receipts (updated to current best practices)
  - Integration examples (updated to current framework versions)

  Deprecated items are marked with `[DEPRECATED since v1.x]` and removed
  after two major versions.

  ---

  ## 8. Editor

  **Harold Nunes** — OMNIX QUANTUM LTD, UAE/UK.

  The Editor is responsible for:
  - RFC lifecycle decisions (ratification, rejection)
  - Conformance vector quality
  - IMPLEMENTATIONS.md maintenance
  - Security response

  Contact: via [GitHub Issues](https://github.com/Costenho19/atf-protocol-standard/issues)
  or the [OMNIX QUANTUM](https://omnixquantum.com) institutional contact.

  ---

  ## 9. License

  The ATF Protocol Standard is published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

  You may implement, extend, or build upon ATF in any software (open or proprietary)
  provided you attribute: *"Based on the ATF Protocol Standard by OMNIX QUANTUM LTD"*.

  Reference implementations and tooling are published under the same license.

  ---

  *This governance model is itself governed by the RFC process. Changes require
  a 30-day review period and Editor ratification.*
  