# @atf-protocol/verifier

  TypeScript port of the ATF Protocol offline receipt verifier.

  Verifies **Agent Trust Fabric** Delegation Receipts (DR) and Runtime Continuity
  Records (RCR) entirely offline — no network access, no platform dependency.

  **Part of the [ATF Protocol Standard](https://github.com/Costenho19/atf-protocol-standard)**

  [![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-RFC--ATF--2-blue?style=flat-square)](https://github.com/Costenho19/atf-protocol-standard/releases/tag/v2.0.0)
  [![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

  ---

  ## Install

  ```bash
  npm install @atf-protocol/verifier

  # Optional: ML-DSA-65 PQC signature verification
  npm install @noble/post-quantum
  ```

  ---

  ## Quick Start

  ```typescript
  import { verifyDelegationReceipt, verifyRuntimeContinuityRecord } from "@atf-protocol/verifier";

  // Verify a Delegation Receipt
  const dr = {
    delegation_id: "ATFDR-AABBCCDDEEFF0011",
    atf_version: "1.0",
    receipt_type: "delegation_receipt",
    issuer_id: "HUMAN-principal-001",
    delegate_id: "AID-TEST-AABBCCDDEEFF0011",
    chain_root_id: "ATFDR-AABBCCDDEEFF0011",
    delegation_depth: 1,
    authority_budget_delegator: 100.0,
    authority_budget_granted: 60.0,
    task_scope: { action: "analyze", asset: "portfolio_x" },
    issued_at: "2026-05-16T10:00:00Z",
    expires_at: "2099-12-31T23:59:59Z",
    content_hash: "sha256:...",    // recomputed by verifier
    pqc_signature: "...",          // ML-DSA-65 base64
    pqc_algorithm: "ML-DSA-65",
  } as const;

  const result = verifyDelegationReceipt(dr);
  // result.verdict === "PASS"
  // result.checks.marInvariant.ok === true  (ATF-INV-001)
  // result.checks.temporalValidity.ok === true  (ATF-INV-006)

  // With PQC signature verification (requires @noble/post-quantum)
  const resultWithSig = verifyDelegationReceipt(dr, {
    publicKeyB64: "<issuer-ml-dsa-65-public-key-base64>",
  });
  ```

  ---

  ## API

  ### `verifyDelegationReceipt(receipt, options?)`

  Verifies a Delegation Receipt (RFC-ATF-1).

  **Invariants enforced:**
  - ATF-INV-001 — Monotonic Authority Reduction (MAR)
  - ATF-INV-002 — Delegation ID format
  - ATF-INV-003 — Chain root integrity
  - ATF-INV-004 — Content hash coverage
  - ATF-INV-006 — Temporal validity

  **Returns:** `ReceiptVerificationResult`

  ### `verifyRuntimeContinuityRecord(rcr, options?)`

  Verifies a Runtime Continuity Record (RFC-ATF-2).

  **Additional invariants enforced:**
  - RGC-INV-001 — TAR presence
  - RGC-INV-002 — CES formula integrity (T×0.30 + B×0.30 + D×0.20 + I×0.20)
  - RGC-INV-003 — Status-CES consistency
  - RGC-INV-004 — HALT requires escalation_event_id

  **Returns:** `ReceiptVerificationResult`

  ### `verifyChain(receipts, options?)`

  Verifies a delegation chain (sequence of DRs).

  - Checks budget monotonicity across the chain (MAR at each level)
  - Validates `chain_root_id` consistency

  **Returns:** `ChainVerificationResult`

  ### `computeContentHash(receipt)`

  Recomputes the `content_hash` for any ATF receipt.

  **Deterministic (FVP-INV-007):** same input always produces same output.
  Excludes: `content_hash`, `pqc_signature`, `pqc_algorithm`, `_comment`, `_ces_formula`.

  ---

  ## Conformance

  This implementation targets **ATF-RGC-Compliant** (14 invariants, L1–L4).

  | Invariant | Status |
  |---|---|
  | ATF-INV-001 (MAR) | ✅ |
  | ATF-INV-002 (ID format) | ✅ |
  | ATF-INV-003 (chain root) | ✅ |
  | ATF-INV-004 (sig coverage) | ✅ |
  | ATF-INV-005 (offline) | ✅ |
  | ATF-INV-006 (temporal) | ✅ |
  | RGC-INV-001 (tar_id) | ✅ |
  | RGC-INV-002 (CES formula) | ✅ |
  | RGC-INV-003 (status) | ✅ |
  | RGC-INV-004 (HALT) | ✅ |
  | FVP-INV-007 (determinism) | ✅ |

  ---

  ## Design Notes

  ### Why `bigint` for `execution_ns`

  JavaScript `number` is a 64-bit float with 53-bit mantissa. Unix timestamps in
  nanoseconds (used by ATF for `execution_ns`) require 63+ bits of integer precision.
  Using `number` would lose the last ~10 bits, making sub-microsecond distinctions
  impossible. This port uses `bigint` for `execution_ns` to maintain full precision.

  ### Why a built-in SHA-256

  To satisfy ATF-INV-005 (offline verifiability without platform dependency), the
  verifier ships with a pure-TypeScript SHA-256 implementation. This avoids any
  mandatory Node.js or browser crypto API dependency, enabling use in constrained
  environments (Deno, Bun, WASM, edge runtimes).

  For production use in environments where `crypto.subtle` is available, replacing
  the built-in SHA-256 with a WebCrypto call is a valid optimization — but the
  output MUST be identical (FVP-INV-007).

  ### PQC signature verification

  ML-DSA-65 (Dilithium-3) signature verification requires a post-quantum crypto
  library. We recommend [`@noble/post-quantum`](https://github.com/paulmillr/noble-post-quantum)
  as a peer dependency. The core verifier does not hard-depend on it so that
  installations without PQC hardware remain possible (ATF-INV-005 satisfied by
  content hash + MAR verification alone).

  ---

  ## Contributing

  See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for language port guidelines.

  For TypeScript-specific issues, open an issue with the label `port:typescript`.

  ---

  *OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
  