/**
   * @atf-protocol/verifier — ATF Protocol Offline Verifier
   *
   * Verifies Agent Trust Fabric receipts (DR, RCR) offline.
   * RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3
   * Zero external dependencies — standard library only.
   *
   * @example
   * import { verifyReceipt, computeContentHash } from '@atf-protocol/verifier';
   *
   * const receipt = JSON.parse(fs.readFileSync('receipt.json', 'utf8'));
   * const result  = verifyReceipt(receipt);
   * console.log(result.verdict); // "PASS" | "FAIL"
   */

  export { computeContentHash } from './hash';
  export { verifyReceipt, verifyDelegationReceipt, verifyRuntimeContinuityRecord } from './verifier';
  export { cesScoreToStatus, computeCes } from './ces';
  export type {
    DelegationReceipt,
    RuntimeContinuityRecord,
    VerificationReport,
    CheckResult,
    VerifyOptions,
    Verdict,
    ContinuityStatus,
    ReasonCode,
  } from './types';
  