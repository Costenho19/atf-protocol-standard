# Agent Trust Fabric (ATF) — Open Protocol Standard

  **OMNIX QUANTUM LTD** · Harold Nunes, Editor · May 2026

  [![Open Standard](https://img.shields.io/badge/Standard-Open%20Spec-blue?style=flat-square)](https://github.com/Costenho19/atf-protocol-standard)
  [![PQC Algorithm](https://img.shields.io/badge/PQC-ML--DSA--65%20(FIPS%20204)-8A2BE2?style=flat-square)](https://csrc.nist.gov/pubs/fips/204/final)
  [![Offline Verifiable](https://img.shields.io/badge/Verification-Offline%20Independent-green?style=flat-square)](./verifier/verify_receipt.py)
  [![Invariants](https://img.shields.io/badge/Invariants-40%20Formal-orange?style=flat-square)](#invariants)
  [![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

  ---

  ## What is ATF?

  **AI agents act. But can you prove who authorized them — and that the authorization was still valid when they acted?**

  The Agent Trust Fabric (ATF) is an open protocol for **cryptographically verifiable AI agent authority governance**. It solves three problems that every regulated AI deployment faces:

  | Problem | ATF Solution |
  |---|---|
  | No proof of who authorized an agent action | Delegation Receipts — PQC-signed, chain-traceable to a human principal |
  | Authorization may expire or degrade mid-execution | Runtime Continuity Records — continuous authority health at nanosecond precision |
  | Evidence is not independently verifiable by regulators | Forensic-grade archive pipeline + self-contained Evidence Packages |

  **Any auditor with the issuer's public key can verify the complete authority chain — no access to OMNIX infrastructure required.**

  ---

  ## The Protocol Stack

  | Layer | Artifact | Standard | Invariants |
  |---|---|---|---|
  | L1 | Agent Identity Record (AIR) | RFC-ATF-1 | ATF-INV-001–006 |
  | L2 | Delegation Receipt (DR) | RFC-ATF-1 | ATF-INV-001–006 |
  | L3 | Temporal Admissibility Record (TAR) | RFC-ATF-1 | ATF-INV-006 |
  | L4 | Runtime Continuity Record (RCR) | RFC-ATF-2 | RGC-INV-001–008 |
  | L5 | Evidence Package (OEP) + GPIL + EAP | RFC-ATF-3 | 26 new invariants |

  **40 total formally specified invariants** across three RFCs.  
  Algorithm: **ML-DSA-65** (Dilithium-3, FIPS 204) — post-quantum secure against both classical and quantum adversaries.

  ---

  ## Standards

  ### RFC-ATF-1 — Verifiable AI Agent Authority Delegation
  Defines the cryptographic foundation: Agent Identity Records, Delegation Receipts, Trust Lattice, Monotonic Authority Reduction (MAR), and the six core invariants (ATF-INV-001–006).

  - **Status:** Published
  - **DOI:** [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
  - **SSRN:** [6757339](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339)
  - **Specification:** [RFC-ATF-1.md](./RFC-ATF-1.md)

  ### RFC-ATF-2 — Runtime Governance Continuity
  Extends RFC-ATF-1 to cover long-running agent executions: Continuity Eligibility Score (CES), Authority Fragmentation Guard (AFG), Escalation Protocol, and Reauthorization Challenge (RC).

  - **Status:** Published — SSRN 6763978
  - **SSRN:** [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
  - **Extends:** RFC-ATF-1
  - **Specification:** [RFC-ATF-2.md](./RFC-ATF-2.md)

  ### RFC-ATF-3 — Governance Policy Interoperability, Evidence Lifecycle & Forensic Verification
  Adds Layer 5 — Forensic Evidence Infrastructure: policy interoperability across sovereign runtimes (GPIL), evidence lifecycle classification with HOT/WARM/COLD tiers (ELR), immutable Merkle archive pipeline (EAP), self-contained forensic packages (OEP), and the key identity verification protocol (FVP).

  - **Status:** Published — May 2026
  - **Extends:** RFC-ATF-1 + RFC-ATF-2
  - **New compliance designation:** ATF-FEI-Compliant
  - **Specification:** [RFC-ATF-3.md](./RFC-ATF-3.md)

  ---

  ## Quick Start

  **Verify a delegation receipt offline (no platform access required):**

  ```bash
  pip install pypqc
  python verifier/verify_receipt.py examples/delegation_receipt.json
  ```

  **Run the test suite:**

  ```bash
  pip install pytest pypqc
  pytest tests/ -v
  ```

  **Validate a receipt against the JSON Schema:**

  ```bash
  pip install jsonschema
  python -c "
  import json, jsonschema
  schema = json.load(open('schemas/delegation_receipt.schema.json'))
  receipt = json.load(open('examples/delegation_receipt.json'))
  jsonschema.validate(receipt, schema)
  print('VALID')
  "
  ```

  ---

  ## Repository Structure

  ```
  atf-protocol-standard/
  ├── RFC-ATF-1.md          ← Delegation protocol (6 invariants)
  ├── RFC-ATF-2.md          ← Runtime continuity (8 invariants)
  ├── RFC-ATF-3.md          ← Evidence lifecycle & forensic verification (26 invariants)
  ├── examples/
  │   ├── delegation_receipt.json         ← RFC-ATF-1: DR example
  │   ├── temporal_authority_record.json  ← RFC-ATF-1: TAR example
  │   └── runtime_continuity_record.json  ← RFC-ATF-2: RCR example
  ├── schemas/
  │   ├── delegation_receipt.schema.json          ← JSON Schema for DR
  │   └── runtime_continuity_record.schema.json   ← JSON Schema for RCR
  ├── verifier/
  │   └── verify_receipt.py     ← Standalone offline verifier (pypqc only)
  └── tests/
      └── test_atf_receipts.py  ← Protocol conformance tests
  ```

  ---

  ## Invariants

  | Family | IDs | RFC | Description |
  |---|---|---|---|
  | ATF-INV | 001–006 | RFC-ATF-1 | Delegation, signing, MAR, verifiability |
  | RGC-INV | 001–008 | RFC-ATF-2 | Continuity, CES, AFG, HALT propagation |
  | GPIL-INV | 001–003 | RFC-ATF-3 | Policy interoperability taxonomy |
  | ELR-INV | 001–004 | RFC-ATF-3 | Evidence lifecycle retention |
  | EAP-INV | 001–007 | RFC-ATF-3 | Archive pipeline integrity |
  | OEP-INV | 001–006 | RFC-ATF-3 | Evidence package completeness |
  | FEA-INV | 001–005 | RFC-ATF-3 | Export authentication |
  | FVP-INV | 007 | RFC-ATF-3 | Forensic verification key identity |
  | **TOTAL** | **40** | | |

  ---

  ## Compliance Designations

  | Designation | Requirements | Layers |
  |---|---|---|
  | ATF-Compliant | RFC-ATF-1 (6 invariants) | L1–L3 |
  | ATF-RGC-Compliant | RFC-ATF-1 + RFC-ATF-2 (14 invariants) | L1–L4 |
  | ATF-GPI-Aligned | ATF-RGC-Compliant + signed CRGC with counterpart | L1–L4 + cross-runtime |
  | **ATF-FEI-Compliant** | RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3 (40 invariants) | L1–L5 |

  ---

  ## Contact

  standards@omnixquantum.com | https://omnixquantum.com

  © 2026 OMNIX QUANTUM LTD. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  