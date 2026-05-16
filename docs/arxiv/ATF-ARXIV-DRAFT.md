# ATF: A Post-Quantum Cryptographic Protocol for Auditable AI Agent Governance

**Authors:** Harold Alberto Nunes Rodelo  
**Affiliation:** OMNIX QUANTUM LTD, United Arab Emirates / United Kingdom  
**Contact:** contact@omnixquantum.com  
**arXiv Category:** cs.CR (Cryptography and Security); cs.AI (Artificial Intelligence)  
**Draft Date:** 2026-05-16  
**Protocol Version:** ATF v3.2.0

---

## Abstract

We present the **Agent Trust Fabric (ATF)**, an open cryptographic protocol for auditable AI agent governance. ATF defines a four-layer authority stack — Identity, Delegation, Temporal Admissibility, and Runtime Continuity — that allows any agent action to be traced back to a human-authorized root through a chain of post-quantum cryptographically signed receipts. The protocol enforces Monotonic Authority Reduction (MAR): every delegation in the chain grants at most the authority it receives. Runtime sessions are monitored by a Continuity Eligibility Score (CES) that aggregates temporal health, budget health, context fidelity, and integrity into a single [0–100] governance signal. Sessions that drop below CES < 10 are halted deterministically. Evidence is sealed into an immutable OMNIX Evidence Package (OEP) verifiable offline without access to the issuing platform. ATF is formalized in three RFCs (ATF-1, ATF-2, ATF-3) defining 40 named invariants. Reference implementations exist in Python, Rust, and TypeScript. The offline verifier has zero external runtime dependencies. We show that ATF satisfies requirements for auditability, independent verifiability, and institutional accountability in regulatory contexts including the EU AI Act (Article 9).

---

## 1. Introduction

Large-scale deployment of AI agents — systems that autonomously take actions on behalf of human principals — creates a governance gap: it is often impossible to determine, after the fact, whether an agent was authorized to take a specific action at the specific moment it acted, and whether that authorization was validly derived from a human root.

Existing approaches address parts of this problem:

- **OAuth 2.0 and OIDC** [RFC 6749, RFC 7519] solve identity and token delegation but do not model runtime authority continuity or expiry at nanosecond granularity.
- **UCAN** (User Controlled Authorization Networks) [Fission, 2021] introduces capability-based delegation chains but lacks post-quantum security and runtime monitoring.
- **W3C Verifiable Credentials** [VC-DATA-MODEL] handle identity claims but not dynamic runtime governance.
- **MCP (Model Context Protocol)** [Anthropic, 2024] defines tool invocation semantics but does not address the authorization chain or evidence lifecycle.

ATF addresses the complete accountability lifecycle: from authority issuance, through runtime monitoring, to forensic evidence export and independent verification — all with post-quantum cryptographic integrity.

### Problem Statement

Given an AI agent action *A* executed at time *t* on behalf of a human principal *H*, we require:

1. **Authorization traceability**: A chain of signed records showing that every delegation from *H* to the agent was valid at time *t*.
2. **Temporal binding**: The authorization was valid at the *exact nanosecond* of admission, not just "at some point."
3. **Runtime integrity**: The authorization remained valid throughout the session, not just at the start.
4. **Independent verifiability**: The authorization chain can be verified by a third party without access to the issuing platform, using only the signed receipts.
5. **Post-quantum durability**: The signatures remain verifiable as quantum computers become available.

ATF satisfies all five requirements.

---

## 2. Protocol Overview

ATF defines four layers:

```
Layer 1: Identity
  Agent Identity Record (AIR) — stable identifier for each agent
  
Layer 2: Delegation  
  Delegation Receipt (DR) — PQC-signed grant of authority from one agent to another
  
Layer 3: Temporal Admissibility
  Temporal Authority Record (TAR) — nanosecond-precise admission gate
  
Layer 4: Runtime Continuity
  Runtime Continuity Record (RCR) — continuous health monitoring via CES
  
Evidence Layer:
  Evidence Lifecycle Retention (ELR) → Evidence Archive Pipeline (EAP) → OMNIX Evidence Package (OEP)
```

Each record is a JSON document carrying a SHA-256 content hash and a ML-DSA-65 (Dilithium-3, FIPS 204) post-quantum signature. The signature covers all fields except `{content_hash, pqc_signature, pqc_algorithm}`, enabling independent hash verification without the signing key.

---

## 3. Delegation Receipt (RFC-ATF-1)

### 3.1 Structure

A Delegation Receipt (DR) captures a single grant of authority from a delegator agent to a delegate agent:

```json
{
  "delegation_id": "ATFDR-{16 uppercase hex digits}",
  "delegator_id": "AIR-{agent-identifier}",
  "delegate_id": "AIR-{agent-identifier}",
  "chain_root_id": "ATFDR-{root delegation id}",
  "authority_budget_delegator": 100,
  "authority_budget_granted": 75,
  "delegation_depth": 1,
  "scope": ["domain:operation"],
  "domain": "FINANCE",
  "issued_at": "2026-05-16T00:00:00Z",
  "issued_at_ns": 1747353600000000000,
  "expires_at": "2026-06-16T00:00:00Z",
  "expires_at_ns": 1749945600000000000,
  "delegator_public_key": "base64url-encoded-ML-DSA-65-public-key",
  "pqc_algorithm": "ML-DSA-65",
  "pqc_signature": "base64url-encoded-signature",
  "content_hash": "sha256:{64-hex-chars}"
}
```

### 3.2 Monotonic Authority Reduction (MAR)

**Definition (MAR):** For any delegation receipt DR, the authority granted to the delegate must not exceed the authority held by the delegator:

> `authority_budget_granted ≤ authority_budget_delegator`

This is enforced as ATF-INV-001. Any receipt where `authority_budget_granted > authority_budget_delegator` is invalid and must be rejected by all conformant verifiers. Violation raises an `AuthorityExpansionViolation`.

**Corollary:** In any delegation chain of depth *d*, the total authority granted at depth *d* ≤ the root authority at depth 0. Authority is monotonically non-increasing along any chain path.

### 3.3 Content Hash

The content hash is computed as:

```python
excluded = {content_hash, pqc_signature, pqc_algorithm, _comment, _ces_formula, _test_note}
payload = {k: v for k, v in receipt.items() if k not in excluded}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
content_hash = "sha256:" + sha256(canonical.encode("utf-8")).hexdigest()
```

This canonical form is deterministic across all conformant implementations (FVP-INV-007).

### 3.4 Invariants (ATF-INV-001–006)

| Invariant | Description |
|---|---|
| ATF-INV-001 | MAR: `budget_granted ≤ budget_delegator` |
| ATF-INV-002 | DR ID format: `ATFDR-[0-9A-F]{16}` |
| ATF-INV-003 | Chain root integrity: `chain_root_id` present and valid |
| ATF-INV-004 | Content hash covers all non-excluded fields |
| ATF-INV-005 | Offline verifiability: delegator public key embedded in DR |
| ATF-INV-006 | Independent verifiability: no platform access required |

---

## 4. Temporal Authority Record (RFC-ATF-2)

### 4.1 Admission Gate

A Temporal Authority Record (TAR) is the admission gate for a runtime session. It is issued **before** the first execution log entry (TAR-INV-001), binding the session to:

- The exact nanosecond of admission (`execution_ns`)
- The state of the Delegation Receipt at that instant
- The current authority budget remaining

A session whose DR is expired, revoked, or in HALT state at admission time receives a TAR with `admission_status = REJECTED`. A REJECTED TAR is permanently attached to the session record — the rejection is immutable and non-repudiable.

### 4.2 Invariants (TAR-INV-001–005)

| Invariant | Description |
|---|---|
| TAR-INV-001 | TAR issued before first execution log entry |
| TAR-INV-002 | TAR references DR by `delegation_id` |
| TAR-INV-003 | REJECTED TAR cannot be reversed post-issuance |
| TAR-INV-004 | `admission_status` is `ADMITTED` or `REJECTED` |
| TAR-INV-005 | Nanosecond precision in `execution_ns` |

---

## 5. Runtime Continuity and CES (RFC-ATF-2)

### 5.1 Continuity Eligibility Score

Sessions admitted via TAR are monitored continuously via the Runtime Continuity Record (RCR). The Continuity Eligibility Score (CES) is:

**CES = T × 0.30 + B × 0.30 + D × 0.20 + I × 0.20**

Where:

- **T** (Temporal Health) = `(expires_at_ns − now_ns) / (expires_at_ns − issued_at_ns) × 100`
- **B** (Budget Health) = `budget_remaining / budget_admission × 100`
- **D** (Context Fidelity) = `100 − context_drift_pct`
- **I** (Integrity Score) = `max(0, 100 − active_anomalies × 10)`

### 5.2 CES Thresholds and Status Transitions

| CES Range | Status | Action |
|---|---|---|
| [75, 100] | NOMINAL | Continue |
| [50, 75) | MONITORING | Enhanced logging |
| [25, 50) | WARNING | Reauthorization advisory issued |
| [10, 25) | CRITICAL | Reauthorization Challenge (RC) required |
| [0, 10) | HALT | Session terminated, sibling sessions revoked, emergency archive sealed |

**HALT is deterministic**: any CES computation below 10.0 raises a `ContinuityHaltError` regardless of other state. This is enforced as RGC-INV-004.

### 5.3 Invariants (RGC-INV-001–008)

| Invariant | Description |
|---|---|
| RGC-INV-001 | RCR must reference a valid TAR |
| RGC-INV-002 | CES formula is T×0.30+B×0.30+D×0.20+I×0.20 — no deviation permitted |
| RGC-INV-003 | HALT triggers emergency archive seal before session termination |
| RGC-INV-004 | CES < 10.0 triggers HALT deterministically |
| RGC-INV-005 | CES weights sum to 1.0 |
| RGC-INV-006 | Budget monotonicity: `budget_remaining ≤ budget_admission` |
| RGC-INV-007 | Context drift threshold: 25% default, configurable |
| RGC-INV-008 | Reauthorization Challenge (RC) required at CRITICAL |

---

## 6. Evidence Lifecycle and OEP (RFC-ATF-3)

### 6.1 Evidence Classification

All governance evidence is classified into immutable lifecycle tiers:

| Class | Tier | Retention |
|---|---|---|
| Active session | HOT | 0–90 days |
| Completed session | WARM | 90–365 days |
| Archived | COLD | >365 days |
| Regulatory | LEGAL | Indefinite |
| Cryptographic receipt | PQC | Indefinite |
| Contractual | CONTRACT | Indefinite |
| Anomaly or HALT event | EXCEPTION | Indefinite |

Classification is immutable after assignment (ELR-INV-003).

### 6.2 OMNIX Evidence Package (OEP)

An OEP is a self-contained, ZIP-format archive containing:

- Full receipt chain (DR + TAR + RCRs)
- Archive manifest with Merkle root
- Lifecycle metadata
- Independent verification instructions

OEPs are verifiable offline by any party with access to `verifier/verify_oep_package.py` and the issuer's public key. No access to OMNIX infrastructure is required (FEA-INV-005).

---

## 7. Cryptographic Analysis

### 7.1 Signature Algorithm

ATF uses **ML-DSA-65** (Dilithium-3, NIST FIPS 204) for all receipt signatures. ML-DSA-65 provides:

- Security level: NIST Level 3 (comparable to AES-192)
- Signature size: 3,293 bytes
- Public key size: 1,952 bytes
- Quantum resistance: based on Module Lattice assumptions (MLWE/MSIS)

The algorithm is standardized by NIST (FIPS 204, August 2024), making ATF receipts verifiable against the permanent public standard.

### 7.2 Hash Function

SHA-256 is used for content integrity. The canonical form ensures byte-identical output across all conformant implementations (Python, Rust, TypeScript, browser WASM). This property — **cross-language hash parity** — is normatively required by FVP-INV-007.

### 7.3 Replay Prevention

Receipts carry `expires_at_ns` (nanosecond epoch), enforced by TAR during admission. Redis-backed anti-replay (configurable via `OMNIX_ANTI_REPLAY_MODE`) prevents replay across distributed nodes.

---

## 8. Implementation and Portability

### 8.1 Reference Implementation

The Python reference implementation (`reference-implementation/`) provides:

- `DelegationReceipt` — MAR-enforcing DR issuance
- `TemporalAuthorityRecord` — nanosecond-precise admission
- `RuntimeContinuityRecord` — CES computation and HALT
- `verify_receipt()` — offline verification (zero external deps)

Install: `pip install atf-protocol`

### 8.2 Language Ports

| Language | Package | Install |
|---|---|---|
| Python | `atf-protocol` (PyPI) | `pip install atf-protocol` |
| TypeScript | `@atf-protocol/verifier` (npm) | `npm install @atf-protocol/verifier` |
| Rust | `atf-verifier` (crates.io) | `cargo add atf-verifier` |

All three ports produce byte-identical SHA-256 hashes for the same receipt (FVP-INV-007), verified by the conformance test suite.

### 8.3 Framework Integrations

| Framework | Package | Capability |
|---|---|---|
| FastAPI | `atf-fastapi` | ATFMiddleware + `require_atf()` dependency |
| LangChain | `atf-langchain` | ATFCallbackHandler + ATFGovernedRunnable |
| OpenAI Agents SDK | `atf-openai-agents` | ATFAgentGuard + ATFHandoffGuard |

### 8.4 Cross-Language Hash Parity

A critical property of ATF is that the canonical SHA-256 content hash is identical across all language implementations. This is verified by the conformance test suite:

```bash
# Python reference
python -c "from atf_core.verifier import compute_content_hash; import json; \
    r = json.load(open('examples/delegation_receipt.json')); print(compute_content_hash(r))"

# TypeScript
npx atf-verify examples/delegation_receipt.json --hash-only

# Rust
./ports/rust/target/release/verify_receipt examples/delegation_receipt.json --hash-only
```

All three must produce the same `sha256:` value.

---

## 9. Performance

Runtime measurements on the OMNIX production runtime (observed during live audit, 2026-05-16):

| Component | Metric | Value |
|---|---|---|
| Scope Admission Engine (SAE) | p50 latency | < 0.1 ms |
| SAE | p99 latency | < 1.2 ms |
| CES computation | CPU-only | < 2 ms |
| DR verification (Python) | Single receipt | < 5 ms |
| DR verification (TS browser) | WebCrypto SHA-256 | < 5 ms |
| OEP archive verification | 10 MB package | < 500 ms |
| Insurance governance cycle | 6 decisions | 3 ms |
| Robotics governance cycle | 9 decisions | 4 ms |

The system sustains concurrent simulation of 8+ industry verticals (finance, insurance, real estate, robotics, medical, defense, energy, quantum) with zero cross-domain interference.

---

## 10. Conformance

ATF defines three conformance profiles:

| Profile | Requirements |
|---|---|
| ATF-Compliant | ATF-INV-001–006: DR chain, MAR, hash, PQC signature |
| ATF-RGC-Compliant | ATF-Compliant + RGC-INV-001–008: TAR, RCR, CES |
| ATF-FEI-Compliant | ATF-RGC-Compliant + evidence lifecycle + OEP export |

Implementations can self-attest conformance using the 66-vector conformance test suite (`tests/test_conformance_vectors.py`).

---

## 11. Related Work

**UCAN** [Brooklyn Zelenka et al., 2021] introduces capability-based delegation with JWT bearer tokens. ATF differs in: (1) post-quantum signatures, (2) runtime continuity monitoring via CES, (3) evidence lifecycle with OEP, (4) nanosecond temporal binding.

**OAuth 2.0 Token Exchange** [RFC 8693] enables delegation but does not model authority budget monotonicity or runtime governance.

**W3C Verifiable Credentials** [VC-DATA-MODEL 1.1] defines credential schema standards. ATF DRs are compatible with VC semantics but extend them with governance-specific invariants.

**CapBAC** [Hernández-Ramos et al., 2016] addresses capability-based access control for IoT. ATF provides similar monotonicity guarantees with cryptographic evidence sealing.

**EU AI Act Article 9** (Risk Management Systems) requires traceability of high-risk AI decisions. ATF's DR chain provides a technically precise interpretation of this requirement.

**NIST AI RMF** [NIST AI 100-1] defines AI governance functions (GOVERN, MAP, MEASURE, MANAGE). ATF implements the GOVERN function at the protocol level.

---

## 12. Conclusion

ATF provides a cryptographically grounded, institutionally presentable foundation for AI agent governance. It answers the question: *"Was this AI agent authorized to take this action at this exact moment?"* with a chain of post-quantum signed receipts that any third party can verify offline.

The 40 named invariants, three RFCs, and multi-language implementation make ATF suitable for regulatory submissions, enterprise deployment, and academic citation. The protocol is designed to be adopted independently of any specific AI platform.

**Repository:** https://github.com/Costenho19/atf-protocol-standard  
**Online Verifier:** https://costenho19.github.io/atf-protocol-standard/verify/  
**PyPI:** `pip install atf-protocol`  
**npm:** `npm install @atf-protocol/verifier`

---

## References

[1] NIST FIPS 204. *Module-Lattice-Based Digital Signature Standard (ML-DSA).* August 2024.  
[2] Fission Codes. *UCAN: User Controlled Authorization Networks.* 2021. https://ucan.xyz  
[3] Hardt, D. *The OAuth 2.0 Authorization Framework.* RFC 6749, IETF, 2012.  
[4] Jones, M. et al. *JSON Web Token (JWT).* RFC 7519, IETF, 2015.  
[5] Jones, M. et al. *OAuth 2.0 Token Exchange.* RFC 8693, IETF, 2020.  
[6] W3C. *Verifiable Credentials Data Model 1.1.* W3C Recommendation, 2022.  
[7] European Parliament. *EU Artificial Intelligence Act.* Regulation (EU) 2024/1689.  
[8] NIST. *Artificial Intelligence Risk Management Framework (AI RMF 1.0).* NIST AI 100-1, 2023.  
[9] Hernández-Ramos, J. L. et al. *Toward a Lightweight Authentication and Authorization Framework for Smart Objects.* IEEE Journal on Selected Areas in Communications, 2016.  
[10] Bernstein, D. J., Lange, T. *Post-quantum cryptography.* Nature, 549, 188–194, 2017.

---

*Submitted for arXiv preprint. Target: cs.CR + cs.AI.*  
*Protocol standard: https://github.com/Costenho19/atf-protocol-standard*  
*Version: ATF v3.2.0 — RFC-ATF-1/2/3 — 40 invariants — Python/Rust/TypeScript*
