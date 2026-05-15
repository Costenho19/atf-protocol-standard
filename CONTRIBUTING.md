# Contributing to ATF Protocol Standard

  Thank you for your interest in the Agent Trust Fabric (ATF) protocol.

  ## How to Contribute

  ### Reporting Issues
  Open a GitHub Issue for:
  - Ambiguities or inconsistencies in the RFC text
  - Gaps in invariant coverage
  - Proposed new invariant families
  - Errors in examples or schemas

  ### Pull Requests

  #### Conformance Tests
  Add test cases to `tests/test_atf_receipts.py` covering edge cases not yet in the existing suite.
  Each test must reference the specific invariant it exercises (e.g., `# ATF-INV-001`).

  #### Reference Implementation
  Contributions to `reference-implementation/` are welcome:
  - Bug fixes in invariant verification logic
  - Additional helper functions
  - New receipt types as the protocol evolves

  #### Language Ports
  We particularly welcome ports in:
  - **Go** — `reference-implementation-go/`
  - **TypeScript/Node.js** — `reference-implementation-ts/`
  - **Rust** — `reference-implementation-rust/`

  Port requirements:
  1. Implement all invariants from RFC-ATF-1 and RFC-ATF-2
  2. Pass JSON interoperability test (verify receipts produced by the Python reference implementation)
  3. Include `README.md` with build and test instructions

  #### Schema Extensions
  Propose new JSON Schemas via Issue first, then submit a PR with:
  - The schema file in `schemas/`
  - At least one example in `examples/`
  - A corresponding conformance test in `tests/`

  ## Code of Conduct

  This is a technical standards repository. Contributions must be:
  - **Technically precise** — vague language weakens invariants
  - **Protocol-neutral** — no vendor-specific assumptions
  - **Traceable** — every design decision references the relevant RFC section

  ## Governance

  The ATF protocol is maintained by **OMNIX QUANTUM LTD**.
  Significant changes to invariants require a new RFC revision.
  Bug fixes and clarifications are applied as errata without a new RFC.

  Contact: standards@omnixquantum.com
  