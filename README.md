# Agent Trust Fabric (ATF) — Open Standards

**OMNIX QUANTUM LTD** · Harold Nunes, Editor · May 2026

This repository contains the official specifications of the Agent Trust Fabric (ATF) protocol stack — open standards for verifiable, post-quantum-secured AI agent authority governance.

---

## Standards

### RFC-ATF-1: Agent Trust Fabric — Verifiable AI Agent Authority Delegation
- **Status:** Published
- **DOI:** [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
- **SSRN:** [6757339](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339)
- **Specification:** [RFC-ATF-1.md](./RFC-ATF-1.md)

### RFC-ATF-2: Agent Trust Fabric — Runtime Governance Continuity
- **Status:** Published — SSRN 6763978
- **SSRN:** [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
- **Extends:** RFC-ATF-1
- **Specification:** [RFC-ATF-2.md](./RFC-ATF-2.md)

---

## Protocol Stack

| Layer | Component | Standard |
|---|---|---|
| L1 | Agent Identity Record (AIR) | RFC-ATF-1 |
| L2 | Delegation Receipt (DR) | RFC-ATF-1 |
| L3 | Temporal Authority Record (TAR) | RFC-ATF-1 |
| L4 | Runtime Continuity Record (RCR) | RFC-ATF-2 |

14 total formally model-checkable invariants (ATF-INV-001-006 + RGC-INV-001-008)

Algorithm: ML-DSA-65 (Dilithium-3, FIPS 204) — post-quantum secure.

Contact: standards@omnixquantum.com | https://omnixquantum.com

(c) 2026 OMNIX QUANTUM LTD. CC BY 4.0.
