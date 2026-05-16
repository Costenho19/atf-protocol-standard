# @atf-protocol/verifier

  **ATF Protocol offline verifier — TypeScript/Node.js port**

  Verifies Agent Trust Fabric Delegation Receipts (DR) and Runtime Continuity Records (RCR) offline.
  RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3. **Zero external dependencies**.

  [![ATF-Compliant](https://img.shields.io/badge/ATF--Compliant-v1.0.0-58a6ff?style=flat-square)](https://costenho19.github.io/atf-protocol-standard/conformance/)
  [![npm](https://img.shields.io/badge/npm-%40atf--protocol%2Fverifier-red?style=flat-square)](https://npmjs.com)
  [![License](https://img.shields.io/badge/license-CC--BY--4.0-gold?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

  ---

  ## Install

  ```bash
  npm install @atf-protocol/verifier
  ```

  ## CLI

  ```bash
  npx atf-verify examples/delegation_receipt.json
  npx atf-verify examples/runtime_continuity_record.json --verbose
  ```

  ## Programmatic API

  ```typescript
  import { verifyReceipt, computeContentHash } from '@atf-protocol/verifier';
  import * as fs from 'fs';

  const receipt = JSON.parse(fs.readFileSync('receipt.json', 'utf8'));
  const result  = verifyReceipt(receipt);

  console.log(result.verdict); // "PASS" | "FAIL"

  // Check specific invariants:
  console.log(result.checks['mar_atf_inv_001'].ok);       // ATF-INV-001
  console.log(result.checks['content_hash_mismatch'].ok); // ATF-INV-004
  console.log(result.checks['ces_formula_rgc_inv_002'].ok); // RGC-INV-002

  // Recompute hash (FVP-INV-007 — deterministic):
  const hash = computeContentHash(receipt);
  assert(hash === receipt.content_hash); // ATF-INV-004
  ```

  ## Invariants enforced

  | Function | Invariants |
  |---|---|
  | `verifyDelegationReceipt()` | ATF-INV-001 · 002 · 003 · 004 · 006 |
  | `verifyRuntimeContinuityRecord()` | RGC-INV-001 · 002 · 003 · 004 + ATF-INV-004 |
  | `computeContentHash()` | ATF-INV-004 · FVP-INV-007 |

  ## References

  - RFC-ATF-1: DOI [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
  - RFC-ATF-2: SSRN [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
  - [Protocol Site](https://costenho19.github.io/atf-protocol-standard/)
  