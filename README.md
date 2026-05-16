# Agent Trust Fabric (ATF) — Open Protocol Standard

**OMNIX QUANTUM LTD** · Harold Nunes, Editor · May 2026

[![RFC-ATF-1 DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20155016-blue?style=flat-square)](https://doi.org/10.5281/zenodo.20155016)
[![RFC-ATF-1 SSRN](https://img.shields.io/badge/SSRN-6757339-blue?style=flat-square)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339)
[![RFC-ATF-2 SSRN](https://img.shields.io/badge/SSRN-6763978-blue?style=flat-square)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
[![PQC Algorithm](https://img.shields.io/badge/PQC-ML--DSA--65%20FIPS%20204-8A2BE2?style=flat-square)](https://csrc.nist.gov/pubs/fips/204/final)
[![Offline Verifiable](https://img.shields.io/badge/Verification-Offline%20Independent-green?style=flat-square)](./verifier/verify_receipt.py)
[![Spec Version](https://img.shields.io/badge/Spec-v3.0%20(RFC--ATF--3)-orange?style=flat-square)](./RFC-ATF-3.md)
[![Invariants](https://img.shields.io/badge/Invariants-40%20Formal-orange?style=flat-square)](#invariants)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)
  [![CI](https://github.com/Costenho19/atf-protocol-standard/actions/workflows/ci.yml/badge.svg)](https://github.com/Costenho19/atf-protocol-standard/actions/workflows/ci.yml)
  [![Threat Model](https://img.shields.io/badge/Threat%20Model-Published-red?style=flat-square)](./THREAT_MODEL.md)
[![Conformance Suite](https://img.shields.io/badge/Conformance%20Suite-92%20vectors%20%C2%B7%2040%20invariants-brightgreen?style=flat-square)](./atf-conformance-suite/)
[![Website](https://img.shields.io/badge/Website-costenho19.github.io%2Fatf--protocol--standard-58a6ff?style=flat-square)](https://costenho19.github.io/atf-protocol-standard/)

  > **[📖 Browse the Protocol Website →](https://costenho19.github.io/atf-protocol-standard/)** — RFC Index · Public Verifier · Conformance Program
  
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

## Protocol Architecture

```mermaid
flowchart TD
    HUMAN["👤 Human Principal\n(authorizes agent)"]
    AIR["L1 — Agent Identity Record (AIR)\nUnique agent identity + public key\nRFC-ATF-1 §4"]
    DR["L2 — Delegation Receipt (DR)\nTask scope + authority budget\nPQC-signed by delegator\nRFC-ATF-1 §5"]
    TAR["L3 — Temporal Admissibility Record (TAR)\nDR validity confirmed at execution time\nnanosecond-precise admission timestamp\nRFC-ATF-1 §6"]
    RCR["L4 — Runtime Continuity Record (RCR)\nCES = T×0.30 + B×0.30 + D×0.20 + I×0.20\nSampled throughout execution lifecycle\nRFC-ATF-2"]
    EAP["L5 — Evidence Archive Pipeline (EAP)\nMerkle-chained, immutable receipt log\nHOT → WARM → COLD retention tiers\nRFC-ATF-3"]
    OEP["L5 — Evidence Package (OEP)\nSelf-contained forensic ZIP\nOffline-verifiable by regulators\nRFC-ATF-3"]

    HUMAN -->|"issues"| AIR
    AIR -->|"signs"| DR
    DR -->|"verified at"| TAR
    TAR -->|"sampled during"| RCR
    RCR -->|"archived to"| EAP
    EAP -->|"exported as"| OEP

    style HUMAN fill:#2d5a9e,color:#fff
    style AIR fill:#1a472a,color:#fff
    style DR fill:#1a472a,color:#fff
    style TAR fill:#4a1a72,color:#fff
    style RCR fill:#4a1a72,color:#fff
    style EAP fill:#7a3a00,color:#fff
    style OEP fill:#7a3a00,color:#fff
```

> **ATF-INV-001 (Monotonic Authority Reduction):** Authority budget granted to an agent MUST NOT exceed the delegator's own budget at any delegation depth. Enforced cryptographically at every layer.

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
Algorithm: **ML-DSA-65** (Dilithium-3, FIPS 204) — designed to resist classical and quantum attacks per NIST FIPS 204 (ML-DSA-65).

---

## Standards

### RFC-ATF-1 — Verifiable AI Agent Authority Delegation

Defines the cryptographic foundation: Agent Identity Records, Delegation Receipts, Trust Lattice, Monotonic Authority Reduction (MAR), and the six core invariants (ATF-INV-001–006).

- **Status:** Published
- **DOI:** [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
- **SSRN:** [6757339](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339)
- **Specification:** [RFC-ATF-1.md](./RFC-ATF-1.md)

### RFC-ATF-2 — Runtime Governance Continuity

Extends RFC-ATF-1 for long-running executions: Continuity Eligibility Score (CES), Authority Fragmentation Guard (AFG), Escalation Protocol, and Reauthorization Challenge (RC).

- **Status:** Published
- **SSRN:** [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
- **Extends:** RFC-ATF-1
- **Specification:** [RFC-ATF-2.md](./RFC-ATF-2.md)

### RFC-ATF-3 — Governance Policy Interoperability, Evidence Lifecycle & Forensic Verification

Adds Layer 5 — Forensic Evidence Infrastructure: policy interoperability across sovereign runtimes (GPIL), evidence lifecycle classification with HOT/WARM/COLD tiers (ELR), immutable Merkle archive pipeline (EAP), self-contained forensic packages (OEP), and key identity verification protocol (FVP).

- **Status:** Published — May 2026
- **Extends:** RFC-ATF-1 + RFC-ATF-2
- **New compliance designation:** ATF-FEI-Compliant
- **Specification:** [RFC-ATF-3.md](./RFC-ATF-3.md)

---


  ---

---

## ATF Conformance Suite

The **ATF Conformance Suite** (`atf-conformance-suite/`) is the standalone,
platform-independent verification harness for all 40 ATF invariants
across RFC-ATF-1, RFC-ATF-2, and RFC-ATF-3.

- **92 test vectors** — positive and negative cases for every invariant
- **3 profiles** — `BASE` (6 invariants) · `RGC` (14) · `ALL` (40)
- **Zero dependencies** — Python 3.8+ stdlib only
- **Tamper-detectable results** — every run produces an `ATFCR-*` artifact with SHA-256 integrity

```bash
git clone https://github.com/Costenho19/atf-protocol-standard
cd atf-protocol-standard/atf-conformance-suite
python run_conformance.py --profile ALL --output result.json
```

```
ATF Conformance Suite 1.0.0
Profile:   ATF-FEI-Compliant
Run:       2026-05-16T21:40:35Z
Result ID: ATFCR-FE46C0F921F6EFE4

  ✓ ATF-INV-001--006     16/16 vectors
  ✓ RGC-INV-001--008     20/20 vectors
  ✓ GPIL / ELR / EAP / OEP   42/42 vectors
  ✓ FEA / FVP            12/12 vectors

Verdict:   PASS  (86/86)
Hash:      sha256:fe6f17e8287f562093018245430b0a4e7055065775f62ea2d3df11a0af719d3d
```

Full documentation: [`atf-conformance-suite/README.md`](./atf-conformance-suite/README.md)
Conformance program: [`CONFORMANCE.md`](./CONFORMANCE.md)

---

  ## Why ATF? — Comparison with Alternatives

  | Property | ATF | Open Policy Agent | SPIFFE/SPIRE | JWT / OAuth 2.0 |
  |---|---|---|---|---|
  | Cryptographic delegation chain (who authorized what) | ✅ PQC-signed receipt per action | ❌ Policy only — no per-action proof | ❌ Identity only — no task scope | ❌ Bearer token — no chain |
  | Authority budget monotonicity (MAR) | ✅ ATF-INV-001 — enforced cryptographically | ❌ | ❌ | ❌ |
  | Runtime authority health monitoring | ✅ CES formula sampled nanosecond-precise | ❌ | ❌ | ❌ |
  | Post-quantum cryptography (FIPS 204) | ✅ ML-DSA-65 | ❌ | ❌ | ❌ |
  | Offline regulatory verification (no platform) | ✅ EAP-INV-005 — public key only | ❌ Requires OPA runtime | ❌ Requires SPIRE API | ❌ Requires issuer |
  | Forensic evidence archive | ✅ Merkle-chained OEP | ❌ | ❌ | ❌ |
  | AI agent-native design | ✅ | ❌ | ❌ | ❌ |
  | Published threat model | ✅ [THREAT_MODEL.md](./THREAT_MODEL.md) | Partial | Partial | Partial |

  ATF is **not** a replacement for OPA or SPIFFE. It is a complementary layer:
  OPA decides *whether* an action is authorized; ATF proves *that* it was authorized,
  *by whom*, *with what budget*, and *whether authority remained valid throughout execution*.

  ---

  ## Regulatory Alignment

  ATF is architecturally aligned with — but does not constitute compliance with — the following frameworks:

  | Framework | Requirement | ATF Artifact |
  |---|---|---|
  | **EU AI Act Art. 9** | Human oversight measures for high-risk AI | Delegation Receipt chain traces every agent action to a human principal |
  | **EU AI Act Art. 12** | Record-keeping for high-risk AI systems | Evidence Archive Pipeline (EAP) + OEP forensic packages |
  | **NIST AI RMF PR.AA-06** | AI system authorization | ATF-INV-001 (MAR) — authority budget tracked and bounded |
  | **NIST AI RMF GV.RR** | Risk response governance | RGC escalation protocol — MONITORING → WARNING → CRITICAL → HALT |
  | **ISO/IEC 42001 §9.2** | AI management system audit | OEP self-contained forensic packages — offline-verifiable by regulators |
  | **NIST CSF 2.0 DE.CM** | Continuous monitoring | Runtime Continuity Records — sampled throughout execution lifecycle |

  > ATF provides the **cryptographic evidence layer** that these frameworks require.
  > It does not replace a compliance programme — it makes one auditable.

  ## Quick Start

**Verify a receipt offline (zero platform dependency):**

```bash
pip install pypqc
python verifier/verify_receipt.py examples/delegation_receipt.json
```

**Run the protocol conformance test suite:**

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

**Use the reference implementation:**

```python
from atf_core import create_delegation_receipt, verify_receipt

dr = create_delegation_receipt(
    delegator_id='HUMAN-harold.nunes',
    delegate_id='AID-FINANCE-9B8C7D6E5F4A3B2C',
    task_scope={'action': 'equity_order_execution'},
    budget_granted=60.0,
    budget_delegator=100.0,
)
result = verify_receipt(dr)
print(result['verdict'])  # PASS
```

---

## Repository Structure

```
atf-protocol-standard/
├── RFC-ATF-1.md                         ← Delegation protocol (6 invariants)
├── RFC-ATF-2.md                         ← Runtime continuity (8 invariants)
├── RFC-ATF-3.md                         ← Evidence lifecycle & forensic (26 invariants)
├── examples/
│   ├── delegation_receipt.json
│   ├── temporal_authority_record.json
│   └── runtime_continuity_record.json
├── schemas/
│   ├── delegation_receipt.schema.json
│   └── runtime_continuity_record.schema.json
├── verifier/
│   └── verify_receipt.py                ← Standalone offline verifier (pypqc only)
├── tests/
│   └── test_atf_receipts.py             ← Conformance tests (MAR, CES, tamper)
├── reference-implementation/
│   ├── README.md
│   ├── pyproject.toml
│   └── atf_core/
│       ├── __init__.py
│       ├── receipts.py                  ← DR + RCR creation with invariant enforcement
│       └── verifier.py                  ← Invariant verification
└── CONTRIBUTING.md
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


  ---

  ## Example Integrations

  ### Python — Issue and Verify a Delegation Receipt

  ```python
  from atf_core import create_delegation_receipt, verify_receipt

  # Human principal delegates authority to an AI agent
  dr = create_delegation_receipt(
      delegator_id="HUMAN-harold-nunes-001",
      delegate_id="AID-UAE-20260516-AABBCCDDEEFF0011",
      task_scope={"action": "governance_decision", "domain": "trading"},
      budget_granted=0.75,       # agent gets 75% of principal's budget
      budget_delegator=1.0,      # principal has full budget
  )

  # Verify the receipt independently (offline, no platform needed)
  result = verify_receipt(dr)
  assert result["verdict"] == "PASS"
  print(f"DR {dr['delegation_id']}: {result['verdict']}")
  # DR ATFDR-A1B2C3D4E5F60011: PASS
  ```

  ### Python — Runtime Continuity Scoring

  ```python
  from atf_core import create_runtime_continuity_record

  # Sample runtime health mid-execution
  rcr = create_runtime_continuity_record(
      tar_id="ATFTAR-1F2E3D4C5B6A7890",
      delegation_id=dr["delegation_id"],
      agent_id="AID-UAE-20260516-AABBCCDDEEFF0011",
      chain_root_id=dr["chain_root_id"],
      ces_temporal=99.0,    # 99% of time window remaining
      ces_budget=100.0,     # full budget intact
      ces_context=80.0,     # 20% context drift
      ces_integrity=100.0,  # chain integrity perfect
      budget_at_admission=0.75,
      budget_remaining=0.75,
      context_drift_pct=20.0,
  )

  # CES = 99×0.30 + 100×0.30 + 80×0.20 + 100×0.20 = 94.9
  print(f"CES: {rcr['ces_score']} — {rcr['continuity_status']}")
  # CES: 94.9 — NOMINAL
  ```

  ### CLI — Verify a Receipt Offline

  ```bash
  # Verify any ATF receipt from a JSON file
  python verifier/verify_receipt.py receipt.json

  # Output:
  # ✓ Type: DR (Delegation Receipt)
  # ✓ ATF-INV-001 (MAR): budget_granted 0.75 ≤ budget_delegator 1.0
  # ✓ ATF-INV-005: content_hash SHA-256 verified
  # ✓ ATF-INV-006: receipt is independently verifiable
  # VERDICT: PASS
  ```

  ### Browser — Interactive Verifier

  Paste any ATF receipt at **[costenho19.github.io/atf-protocol-standard/verify/](https://costenho19.github.io/atf-protocol-standard/verify/)** — verifies MAR, CES formula, and content hash client-side. No data leaves your browser.

  ## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). We welcome language ports (Go, TypeScript, Rust), conformance test contributions, and feedback on invariant completeness via Issues.

  ## Releases & Changelog

  | Version | RFC | Date | Invariants |
  |---|---|---|---|
  | [v3.0.0](https://github.com/Costenho19/atf-protocol-standard/releases/tag/v3.0.0) | RFC-ATF-3 | May 2026 | 40 total (26 new) |
  | [v2.0.0](https://github.com/Costenho19/atf-protocol-standard/releases/tag/v2.0.0) | RFC-ATF-2 | Mar 2026 | 14 total (8 new) |
  | [v1.0.0](https://github.com/Costenho19/atf-protocol-standard/releases/tag/v1.0.0) | RFC-ATF-1 | Jan 2026 | 6 |

  See [CHANGELOG.md](./CHANGELOG.md) for the full history.

  ## Verifier Tools

  | Tool | Path | Description |
  |---|---|---|
  | Receipt Verifier | [`verifier/verify_receipt.py`](./verifier/verify_receipt.py) | DR + RCR offline verifier — ATF-INV-001–006, RGC-INV-001–004 |
  | OEP Archive Verifier | [`verifier/verify_oep_package.py`](./verifier/verify_oep_package.py) | Forensic ZIP archive verifier — OEP-INV-001–006, EAP-INV-001–007 |

  Both tools have zero dependency on the OMNIX platform (EAP-INV-005).

  ```bash
  pip install pypqc

  # Verify a delegation receipt
  python verifier/verify_receipt.py examples/delegation_receipt.json

  # Verify a full forensic evidence package
  python verifier/verify_oep_package.py evidence_package.zip --public-key issuer.b64
  ```

  ## Conformance Program

  The ATF Conformance Program provides test vectors for each profile.
  See [CONFORMANCE.md](./CONFORMANCE.md) for the full program.

  | Profile | Invariants | Test Vectors | Badge |
  |---|---|---|---|
  | `ATF-Compliant` | 6 (L1–L3) | 15 (8 positive, 7 negative) | `[![ATF-Compliant](https://img.shields.io/badge/ATF--Compliant-RFC--ATF--1-blue?style=flat-square)]` |
  | `ATF-RGC-Compliant` | 14 (L1–L4) | 26 (14 positive, 12 negative) | `[![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-RFC--ATF--2-blue?style=flat-square)]` |
  | `ATF-FEI-Compliant` | 40 (L1–L5) | 34 (18 positive, 16 negative) | `[![ATF-FEI-Compliant](https://img.shields.io/badge/ATF--FEI--Compliant-RFC--ATF--3-blue?style=flat-square)]` |

  ## Language Ports

  | Language | Package | Status | Invariants |
  |---|---|---|---|
  | **Python** (reference) | [`reference-implementation/`](./reference-implementation/) | ✅ Stable | ATF-Compliant + ATF-RGC-Compliant |
  | **TypeScript** | [`ports/typescript/`](./ports/typescript/) | ✅ Stable | ATF-RGC-Compliant (11 invariants) |
  | Go | — | ❌ Wanted | [Contribute](./CONTRIBUTING.md) |
  | Rust | — | ❌ Wanted | [Contribute](./CONTRIBUTING.md) |

---


  ---

  ## Protocol Scope and Boundaries

  ATF specifies cryptographic and protocol mechanisms for three things:

  1. **Delegating agent authority** — from a human principal to an AI agent, with PQC-signed, chain-traceable receipts (RFC-ATF-1)
  2. **Monitoring authority health at runtime** — continuous CES scoring, HALT propagation, escalation (RFC-ATF-2)
  3. **Archiving and verifying the resulting evidence** — lifecycle classification, Merkle-chained archive, self-contained forensic packages (RFC-ATF-3)

  **ATF explicitly does NOT specify:**

  | Out of Scope | Notes |
  |---|---|
  | Pre-execution authority resolution | Whether an action *should* be authorized is outside ATF — ATF records what *was* authorized and that it was still valid |
  | AI model selection or safety constraints | ATF is model-agnostic |
  | Real-time revocation notification | HALT propagates within a session; inter-session revocation requires out-of-band coordination (see [SECURITY.md](./SECURITY.md)) |
  | Network transport or API protocols | ATF defines receipt formats, not wire protocols |
  | Regulatory compliance | ATF is architecturally aligned with traceability requirements in EU AI Act, NIST AI RMF, and ISO/IEC 42001 — it does not constitute compliance with any of them |

  **Conformance designations are self-declared** based on the test vectors and verification tools in this repository. No third-party certification body is currently designated. See [GOVERNANCE.md](./GOVERNANCE.md) for the conformance claim process.

  ## Contact

standards@omnixquantum.com | https://omnixquantum.com

© 2026 OMNIX QUANTUM LTD. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
