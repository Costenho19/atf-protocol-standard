# ATF Protocol Standard — Public Roadmap

  **Updated:** May 2026 · **Editor:** Harold Nunes, OMNIX QUANTUM LTD

  ---

  ## Context & Goals

  ### The Problem

  Modern AI systems can log actions,
  but most cannot independently prove that authority remained valid throughout execution.

  Organizations therefore struggle to verify:
  - who authorized an action,
  - whether delegation remained valid at runtime,
  - and whether evidence can survive platform failure or organizational boundary crossing.

  ### ATF Goal

  ATF defines an open protocol for:
  - cryptographically verifiable delegation,
  - runtime authority continuity,
  - forensic evidence portability,
  - and offline governance verification.

  The protocol is designed to remain implementation-independent, interoperable,
  and auditable across organizational boundaries.

  ### Ecosystem Objectives

  The ATF roadmap focuses on:
  - independent verifier portability,
  - cross-language determinism,
  - public conformance testing,
  - third-party implementations,
  - and long-term governance interoperability.

  ---

  ## Adoption Signals

  Protocol maturity is measured by ecosystem adoption and cross-platform reproducibility —
  not download counts.

  | Signal | Indicator |
  |---|---|
  | Independent implementations | Third-party verifiers registered in IMPLEMENTATIONS.md |
  | Public conformance runs | Verifiable `ATFCR-*` result IDs from the standalone conformance suite |
  | Cross-language determinism | Identical verdicts across Python, Rust, TypeScript, and Go |
  | External protocol integrations | ATF receipts referenced in non-OMNIX production systems |
  | Academic or technical citations | RFC-ATF-1, RFC-ATF-2, or RFC-ATF-3 cited in external work |
  | Regulatory alignment | ATF artifacts referenced in regulatory or compliance submissions |
  | Conformance testing service usage | CI runs against the hosted conformance suite |

  ---

  ## Completed (v1.0.0 – v3.0.0)

  | Item | Status | Details |
  |---|---|---|
  | RFC-ATF-1: Agent Trust Fabric Delegation Protocol | ✅ | Published · DOI: 10.5281/zenodo.20155016 |
  | RFC-ATF-2: Runtime Governance Continuity Protocol | ✅ | Published · DOI: 10.5281/zenodo.20241344 · SSRN: 6763978 |
  | RFC-ATF-3: Evidence Lifecycle & Forensic Verification | ✅ | Published · May 2026 |
  | 40 formal invariants (ATF + RGC + GPIL + ELR + EAP + OEP + FEA + FVP) | ✅ | 8 invariant families across 3 RFCs |
  | Python reference implementation (`reference-implementation/`) | ✅ | pyproject.toml · ML-DSA-65 signing |
  | Offline verifier CLI (`verifier/verify_receipt.py`) | ✅ | Zero external deps · stdlib only |
  | ATF Conformance Suite (`atf-conformance-suite/`) | ✅ | 92 vectors · all 40 invariants · signed ATFCR results |
  | GitHub Pages site (8 pages) | ✅ | Whitepaper · Verifier · Quickstart · Integrations · Diagrams |
  | Rust port — complete verifier (`ports/rust/`) | ✅ | All conformance tests pass |
  | Threat model audit (THREAT_MODEL.md) | ✅ | 13 vectors · 4 fixes · 9 documented |
  | LangChain integration (`integrations/langchain/`) | ✅ | ATF-RGC-Compliant |
  | FastAPI middleware (`integrations/fastapi/`) | ✅ | ATF-Compliant |
  | OpenAI Agents SDK wrapper (`integrations/openai-agents/`) | ✅ | ATF-Compliant |

  ---

  ## Near-term (Q3 2026)

  ### TypeScript port (`ports/typescript/`)
  Port the reference verifier to TypeScript/Node.js for use in AI agent frameworks
  and browser-based verification tools.
  - `src/hash.ts` — canonical JSON serialization + SHA-256
  - `src/verifier.ts` — DR + RCR chain verification
  - `src/cli.ts` — CLI entry point (`npx atf-verify receipt.json`)
  - Published to npm as `@atf-protocol/verifier`
  - Target: full 92-vector conformance suite passing across all three profiles

  ### PyPI publication (`pip install atf-verifier`)
  Publish the standalone verifier as a zero-dependency PyPI package.
  - `pip install atf-verifier`
  - CLI entry point: `atf verify receipt.json`
  - Enables `python run_conformance.py --profile ALL` without cloning the repository
  - Milestone: listed in PyPI under the `ai-governance` classifier

  ### arXiv preprint (cs.CR)
  Submit a formal arXiv paper in the Cryptography and Security category.
  - Title: *"ATF: A Post-Quantum Cryptographic Framework for AI Agent Authority Delegation"*
  - Cites RFC-ATF-1 DOI (Zenodo), RFC-ATF-2 (SSRN), FIPS 204, NIST AI RMF 1.0
  - Establishes academic record prior to IETF submission

  ---

  ## Medium-term (Q4 2026)

  ### Go port (`ports/go/`)
  Port the verifier to Go for cloud-native and infrastructure integration use cases.
  - `atf-verifier` module published to pkg.go.dev
  - Idiomatic Go — interfaces, structured errors, context propagation
  - Full 92-vector conformance suite passing

  ### First external implementation
  Integration of ATF receipts into a production AI governance system
  by a party independent of OMNIX QUANTUM.
  - Registers in IMPLEMENTATIONS.md with a verifiable `ATFCR-*` conformance result
  - Documents any implementation divergence via the protocol errata process
  - Provides a reproducible cross-platform interoperability data point

  ### RFC-ATF-4 (draft): Multi-Runtime Governance Policy Federation
  Specify how multiple ATF-compliant runtimes federate their governance policies
  across organizational and jurisdictional boundaries.
  - Extends GPIL (RFC-ATF-3 §4)
  - Introduces a federated policy registry with cross-domain trust propagation
  - Designed for multi-cloud, multi-jurisdiction regulated AI deployments

  ---

  ## Long-term (2027+)

  ### IETF Internet-Draft
  Submit an Informational Internet-Draft to the IETF describing the ATF delegation model.
  - Builds on the existing RFC-ATF-1 Zenodo DOI as prior art
  - Target working group: SAAG (Security Area Advisory Group) or a dedicated AI governance WG
  - Engages the standards community in open editorial process

  ### Formal model checking (TLA+ — complete)
  Complete the TLA+ formal specification beyond the 5 currently model-checked properties.
  - Full HALT protocol state machine model
  - Deadlock-freedom proof for the RCR predecessor chain
  - Published as a versioned annex to RFC-ATF-2

  ### Hosted conformance testing service
  A hosted GitHub Action and API that tests implementations against the ATF Conformance Suite
  on every push, returning a tamper-detectable `ATFCR-*` result artifact.
  - Integrates with IMPLEMENTATIONS.md automatically
  - Issues signed conformance badges for verified implementations

  ---

  ## Not planned

  The following are explicitly **out of scope** for the ATF protocol:

  - **Centralized agent registry**: ATF is platform-independent. A central registry would violate ATF-INV-006 (temporal authority independence).
  - **Runtime execution engine**: ATF specifies governance receipts, not execution semantics. What agents *do* is out of scope.
  - **Proprietary extensions**: All protocol extensions must follow the RFC process. Proprietary forks are permitted under CC BY 4.0 but will not be accepted into the conformance suite or IMPLEMENTATIONS.md.
  - **Backward-incompatible receipt formats**: All receipt format changes require a new RFC version. Existing signed receipts must remain verifiable indefinitely.

  ---

  ## How to contribute

  See [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md).

  For roadmap feedback, open a [GitHub Issue](https://github.com/Costenho19/atf-protocol-standard/issues)
  with label `roadmap`.

  *OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
  