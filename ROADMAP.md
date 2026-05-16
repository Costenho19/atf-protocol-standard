# ATF Protocol Standard — Public Roadmap

  **Updated:** May 2026 · **Editor:** Harold Nunes

  This roadmap describes the planned evolution of the ATF Protocol Standard.
  Items marked ✅ are complete. Items marked 🔄 are in progress.

  ---

  ## Completed (v1.0.0 – v3.0.0)

  | Item | Status | Details |
  |---|---|---|
  | RFC-ATF-1: Agent Trust Fabric Delegation Protocol | ✅ | Published · DOI: 10.5281/zenodo.20155016 |
  | RFC-ATF-2: Runtime Governance Continuity Protocol | ✅ | Published · SSRN: 6763978 |
  | RFC-ATF-3: Evidence Lifecycle & Forensic Verification | ✅ | Candidate |
  | 40 formal invariants (ATF + RGC + GPIL + ELR + EAP + OEP + FEA + FVP) | ✅ | |
  | Python reference implementation (`reference-implementation/`) | ✅ | pyproject.toml |
  | Offline verifier CLI (`verifier/verify_receipt.py`) | ✅ | Zero external deps |
  | 66 conformance test vectors (CI green) | ✅ | |
  | GitHub Pages site (8 pages) | ✅ | Whitepaper · Verifier · Quickstart · Integrations · Diagrams |
  | Rust port skeleton (`ports/rust/`) | ✅ | cargo check passes |
  | Rust complete verifier (`ports/rust/src/`) | ✅ | All conformance tests pass |
  | LangChain integration (`integrations/langchain/`) | ✅ | ATF-RGC-Compliant |
  | FastAPI middleware (`integrations/fastapi/`) | ✅ | ATF-Compliant |
  | OpenAI Agents SDK wrapper (`integrations/openai-agents/`) | ✅ | ATF-Compliant |

  ---

  ## Near-term (Q3 2026)

  ### TypeScript port (`ports/typescript/`)
  Port the reference verifier to TypeScript/Node.js.
  - `src/hash.ts` — canonical JSON + SHA-256
  - `src/verifier.ts` — DR + RCR verification
  - `src/cli.ts` — CLI entry point (`npx atf-verify receipt.json`)
  - Published to npm as `@atf-protocol/verifier`
  - Target: same 66 conformance vectors passing

  ### PyPI publication (`pip install atf-verifier`)
  Publish the standalone verifier as a PyPI package.
  - `pip install atf-verifier`
  - CLI entry point: `atf verify receipt.json`
  - Zero dependencies (standard library only)
  - Achieves discoverability in PyPI search results

  ### arXiv preprint
  Submit a formal arXiv paper (cs.CR — Cryptography and Security).
  - Title: "ATF: A Post-Quantum Cryptographic Framework for AI Agent Authority Delegation"
  - Cites RFC-ATF-1 DOI, RFC-ATF-2 SSRN, FIPS 204, NIST AI RMF
  - Improves academic discoverability and citation credibility

  ---

  ## Medium-term (Q4 2026)

  ### Go port (`ports/go/`)
  Port the verifier to Go.
  - `atf-verifier` module on pkg.go.dev
  - Idiomatic Go (interfaces, errors)
  - Same conformance suite

  ### First real external adopter
  Work with a partner to integrate ATF into a production AI governance system.
  - Contribute to IMPLEMENTATIONS.md
  - Provide case study for the whitepaper
  - Co-author a joint blog post / technical note

  ### RFC-ATF-4 (draft): Multi-Runtime Governance Policy Federation
  Specify how multiple ATF-compliant runtimes federate their governance policies.
  - Extends GPIL (RFC-ATF-3)
  - Introduces federated policy registry
  - Designed for multi-cloud, multi-jurisdiction AI deployments

  ---

  ## Long-term (2027+)

  ### IETF Internet-Draft
  Submit an Informational RFC to the IETF describing the ATF delegation model.
  - Builds on the existing RFC-ATF-1 DOI
  - Engages the broader standards community
  - Target working group: TBD (SAAG or new AI governance WG)

  ### Formal model checking (TLA+ complete)
  Complete the TLA+ formal specification beyond the 5 currently model-checked properties.
  - Model the full HALT protocol state machine
  - Verify deadlock-freedom for the RCR predecessor chain
  - Publish as part of RFC-ATF-2 v1.1

  ### Conformance testing service
  A hosted service (GitHub Action + API) that automatically tests implementations
  against the conformance suite on each push.

  ---

  ## Not planned

  The following are explicitly **not** planned for ATF:

  - **Centralized registry of agents**: ATF is designed to be platform-independent. A central registry would undermine ATF-INV-006.
  - **Runtime execution engine**: ATF specifies governance receipts, not how agents execute. Execution is out of scope.
  - **Proprietary extensions**: All protocol extensions must go through the RFC process. Proprietary forks are allowed under CC BY 4.0 but will not be included in the conformance suite.

  ---

  ## How to contribute

  See [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md).

  For roadmap feedback, open a [GitHub Issue](https://github.com/Costenho19/atf-protocol-standard/issues)
  with label `roadmap`.
  