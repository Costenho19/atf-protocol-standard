# Changelog — ATF Protocol Standard

  All notable changes to the Agent Trust Fabric protocol standard are documented here.
  Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
  Versioning follows [Semantic Versioning](https://semver.org/).

  ---

  ## [v3.1.0] — 2026-05-16

  ### Added — Verifiers, Conformance Program, TypeScript Port

  #### OEP Archive Verifier (`verifier/verify_oep_package.py`)
  New standalone tool for offline verification of complete forensic evidence packages.
  Covers OEP-INV-001–006 + EAP-INV-001–007. ZIP bomb protection, path traversal guard,
  three-plane verification (structure → cryptographic integrity → semantic chain).
  Generates reproducible evidence transcript (FVP-INV-007).

  #### ATF Conformance Program v1 (`CONFORMANCE.md` + `conformance/conformance_vectors.json`)
  Official conformance program with 34 test vectors across 3 profiles:
  - ATF-Compliant: 15 vectors (8 positive, 7 negative) — ATF-INV-001–006
  - ATF-RGC-Compliant: 26 vectors — + RGC-INV-001–006
  - ATF-FEI-Compliant: 34 vectors — all 40 invariants
  Badge usage, implementation report template, determinism requirement (FVP-INV-007).

  #### TypeScript Port (`ports/typescript/` — `@atf-protocol/verifier`)
  First official TypeScript port of the ATF verifier. Ships with:
  - Inline pure-TS SHA-256 (no crypto API dependency — EAP-INV-005)
  - `bigint` for `execution_ns` (nanosecond precision — avoids JS float precision loss)
  - Stable normative reason codes across all invariants
  - Optional `@noble/post-quantum` for ML-DSA-65 PQC signature verification
  - Targets: ATF-RGC-Compliant (11 invariants)

  #### Verifier API Extension (`verifier/verify_receipt.py`)
  Added `verify_receipt_dict(receipt: dict) -> dict` programmatic API.
  Added `ReasonCode` class with normative reason codes.
  Extended coverage: ATF-INV-002, ATF-INV-003, ATF-INV-006, RGC-INV-001–004.

  #### Infrastructure
  - `tests/test_conformance_vectors.py`: Conformance vector test suite
  - Updated CI to run conformance vectors on every push
  - Updated README with verifier tools table, conformance program, language ports

  ---

  ## [v3.0.0] — 2026-05-15

  ### Added — RFC-ATF-3: Governance Policy Interoperability, Evidence Lifecycle & Forensic Verification

  **New compliance designation:** `ATF-FEI-Compliant`
  **Total invariants:** 40 (26 new across 6 families)

  #### Protocol Families

  - **GPIL — Governance Policy Interoperability Layer** (3 invariants)
    - Cross-runtime policy taxonomy: SOVEREIGN / FEDERATED / DELEGATED / HYBRID
    - Cross-Runtime Governance Contract (CRGC) format

  - **ELR — Evidence Lifecycle Record** (4 invariants)
    - HOT / WARM / COLD retention tier classification
    - Mandatory tier transition rules with retention minimums

  - **EAP — Evidence Archive Pipeline** (7 invariants)
    - Merkle-chained immutable receipt log
    - Archive Root Hash (ARH) with ML-DSA-65 signature
    - EAP-INV-005: offline verifiability without platform access

  - **OEP — OMNIX Evidence Package** (6 invariants)
    - Self-contained forensic ZIP format
    - Machine-readable manifest with schema version

  - **FEA — Forensic Export Authentication** (5 invariants)
    - Export authorization protocol
    - Caller key identity binding

  - **FVP — Forensic Verification Protocol** (1 invariant)
    - FVP-INV-007: verifier determinism requirement

  #### Infrastructure

  - Added `examples/` — 3 complete JSON receipt examples (DR, TAR, RCR)
  - Added `schemas/` — JSON Schemas for DR and RCR (JSON Schema 2020-12)
  - Added `verifier/verify_receipt.py` — standalone offline verifier (pypqc only)
  - Added `tests/test_atf_receipts.py` — protocol conformance test suite
  - Added `reference-implementation/` — installable Python package (`pip install -e .`)
  - Added `CONTRIBUTING.md` — language port guidelines (Go, TypeScript, Rust)
  - Added `.github/workflows/ci.yml` — automated conformance CI
  - Updated `README.md` — Mermaid architecture diagram, DOI/SSRN badges, full invariant table

  ---

  ## [v2.0.0] — 2026-03-01

  ### Added — RFC-ATF-2: Runtime Governance Continuity

  **Compliance designation:** `ATF-RGC-Compliant`
  **Total invariants:** 14 (8 new)

  - **Runtime Continuity Record (RCR)** — L4 protocol artifact
    - PQC-signed authority health snapshot sampled throughout execution
    - `execution_ns` nanosecond-precise timestamping

  - **Continuity Eligibility Score (CES)** — RGC-INV-002
    - Formula: T×0.30 + B×0.30 + D×0.20 + I×0.20
    - Status thresholds: NOMINAL (≥75) / MONITORING (≥50) / WARNING (≥30) / CRITICAL (≥10) / HALT (<10)

  - **Authority Fragmentation Guard (AFG)**
    - Fragmentation score monitoring with configurable threshold
    - Default limit: 0.90 (hard maximum: 0.95)

  - **Escalation Protocol**
    - MONITORING → WARNING → CRITICAL → HALT progression with mandatory recording
    - HALT propagates atomically to all child delegations (RGC-INV-004)

  - **Reauthorization Challenge (RC)**
    - Mechanism to resolve CRITICAL status without HALT

  - **New invariants:** RGC-INV-001 through RGC-INV-008

  **Reference:** SSRN [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)

  ---

  ## [v1.1.0] — 2026-02-01

  ### Added

  - Temporal Admissibility Record (TAR) specification
  - Extended examples for delegation chain scenarios
  - Clarifications on Trust Lattice boundary conditions

  ---

  ## [v1.0.0] — 2026-01-15

  ### Added — RFC-ATF-1: Verifiable AI Agent Authority Delegation

  **Compliance designation:** `ATF-Compliant`
  **Total invariants:** 6

  - **Agent Identity Record (AIR)** — L1
    - Unique cryptographic agent identity binding
    - ML-DSA-65 (Dilithium-3, FIPS 204) key registration

  - **Delegation Receipt (DR)** — L2
    - PQC-signed authority grant with task scope and budget
    - ATF-INV-001 (MAR): budget_granted MUST NOT exceed budget_delegator

  - **Temporal Admissibility Record (TAR)** — L3
    - Nanosecond-precise DR validity proof at execution time

  - **Trust Lattice**
    - Partial order over authority budgets
    - Monotonic Authority Reduction (MAR) enforced at every depth

  - **Core invariants:** ATF-INV-001 through ATF-INV-006

  **Reference:**
  - DOI: [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
  - SSRN: [6757339](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339)

  ---

  *OMNIX QUANTUM LTD · standards@omnixquantum.com*
  *© 2026 CC BY 4.0*
  