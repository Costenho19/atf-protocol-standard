/**
   * ATF Receipt Verifier — TypeScript port.
   *
   * Verifies Delegation Receipts (RFC-ATF-1) and Runtime Continuity Records
   * (RFC-ATF-2) against all applicable invariants.
   *
   * Zero external dependencies — standard library only (EAP-INV-005).
   *
   * @example
   * import { verifyReceipt } from '@atf-protocol/verifier';
   *
   * const receipt = JSON.parse(fs.readFileSync('receipt.json', 'utf8'));
   * const result  = verifyReceipt(receipt);
   *
   * if (result.verdict === 'FAIL') {
   *   const failed = Object.entries(result.checks)
   *     .filter(([, c]) => !c.ok)
   *     .map(([k, c]) => `${k}: ${c.note}`);
   *   console.error('ATF violations:', failed);
   * }
   */

  import { computeContentHash } from './hash';
  import { computeCes, cesScoreToStatus, CES_TOLERANCE } from './ces';
  import type {
    VerificationReport, CheckResult, VerifyOptions, Verdict, ContinuityStatus, ReasonCode
  } from './types';

  /** DR ID pattern: ATFDR-{16 uppercase hex digits} (ATF-INV-002). */
  const DR_ID_PATTERN = /^ATFDR-[0-9A-F]{16}$/;

  function isExampleReceipt(r: Record<string, unknown>): boolean {
    const sig = String(r['pqc_signature'] ?? '');
    return sig.includes('BASE64_') || sig === 'PENDING_SIGNING';
  }

  function deriveVerdict(checks: Record<string, CheckResult>): Verdict {
    return Object.values(checks).some(c => !c.ok) ? 'FAIL' : 'PASS';
  }

  function pass(note?: string): CheckResult { return { ok: true, note }; }
  function fail(reason: ReasonCode, note?: string): CheckResult { return { ok: false, reason, note }; }

  /**
   * Verify any ATF receipt — auto-detects DR vs RCR from field presence.
   */
  export function verifyReceipt(
    receipt: Record<string, unknown>,
    options: VerifyOptions = {},
  ): VerificationReport {
    if ('ces_score' in receipt || 'continuity_status' in receipt) {
      return verifyRuntimeContinuityRecord(receipt, options);
    }
    return verifyDelegationReceipt(receipt, options);
  }

  /**
   * Verify a Delegation Receipt (RFC-ATF-1).
   * Enforces ATF-INV-001, 002, 003, 004, 006.
   */
  export function verifyDelegationReceipt(
    receipt: Record<string, unknown>,
    options: VerifyOptions = {},
  ): VerificationReport {
    const checks: Record<string, CheckResult> = {};
    const notes: string[] = [];
    const did = String(receipt['delegation_id'] ?? '');

    // ATF-INV-002 — Delegation ID format
    if (did && DR_ID_PATTERN.test(did)) {
      checks['id_format_atf_inv_002'] = pass(`delegation_id format valid: ${did}`);
    } else if (!did) {
      checks['id_format_atf_inv_002'] = fail('id_format_atf_inv_002', 'delegation_id missing');
    } else {
      checks['id_format_atf_inv_002'] = fail('id_format_atf_inv_002', `ATF-INV-002: invalid format: ${did}`);
    }

    // ATF-INV-001 — Monotonic Authority Reduction (MAR)
    const granted   = Number(receipt['authority_budget_granted']   ?? 0);
    const delegator = Number(receipt['authority_budget_delegator'] ?? Infinity);
    if (granted <= delegator) {
      checks['mar_atf_inv_001'] = pass(`MAR: ${granted} ≤ ${delegator}`);
      notes.push(`ATF-INV-001 PASS: ${granted}/${delegator}`);
    } else {
      checks['mar_atf_inv_001'] = fail('mar_atf_inv_001',
        `ATF-INV-001 VIOLATION: budget_granted ${granted} > budget_delegator ${delegator}`);
      notes.push(`ATF-INV-001 FAIL: ${granted} > ${delegator}`);
    }

    // ATF-INV-003 — Chain root
    const chainRoot = String(receipt['chain_root_id'] ?? '');
    if (chainRoot) {
      checks['chain_root_atf_inv_003'] = pass(`chain_root_id present: ${chainRoot}`);
    } else {
      checks['chain_root_atf_inv_003'] = fail('chain_root_atf_inv_003', 'ATF-INV-003: chain_root_id missing');
    }

    // ATF-INV-004 — Content hash
    const storedHash   = String(receipt['content_hash'] ?? '');
    const computedHash = computeContentHash(receipt);
    const isExample    = isExampleReceipt(receipt);
    if (isExample) {
      checks['content_hash_mismatch'] = pass('content_hash: SKIP (example receipt)');
    } else if (storedHash === computedHash) {
      checks['content_hash_mismatch'] = pass(`content_hash verified: ${computedHash.slice(0, 40)}...`);
      notes.push(`ATF-INV-004 PASS`);
    } else {
      checks['content_hash_mismatch'] = fail('content_hash_mismatch',
        `ATF-INV-004 FAIL: stored=${storedHash.slice(0,32)} computed=${computedHash.slice(0,32)}`);
    }

    // ATF-INV-006 — Temporal validity
    const expiresAt = String(receipt['expires_at'] ?? '');
    if (!expiresAt) {
      checks['expired_atf_inv_006'] = pass('expires_at: not set');
    } else {
      const exp = new Date(expiresAt);
      const now = options.nowOverride ?? new Date();
      if (isNaN(exp.getTime())) {
        checks['expired_atf_inv_006'] = fail('expired_atf_inv_006', `Cannot parse expires_at: ${expiresAt}`);
      } else if (now <= exp) {
        checks['expired_atf_inv_006'] = pass(`ATF-INV-006 PASS: expires ${expiresAt}`);
      } else {
        checks['expired_atf_inv_006'] = fail('expired_atf_inv_006', `ATF-INV-006 FAIL: DR expired at ${expiresAt}`);
      }
    }

    return {
      receiptId: did,
      receiptType: 'delegation_receipt',
      verdict: deriveVerdict(checks),
      checks,
      notes,
    };
  }

  /**
   * Verify a Runtime Continuity Record (RFC-ATF-2).
   * Enforces RGC-INV-001, 002, 003, 004 + ATF-INV-004.
   */
  export function verifyRuntimeContinuityRecord(
    rcr: Record<string, unknown>,
    options: VerifyOptions = {},
  ): VerificationReport {
    const checks: Record<string, CheckResult> = {};
    const notes: string[] = [];
    const rcrId = String(rcr['rcr_id'] ?? '');

    // RGC-INV-001 — TAR presence
    const tarId = String(rcr['tar_id'] ?? '');
    if (tarId) {
      checks['rgc_inv_001'] = pass(`TAR present: ${tarId}`);
    } else {
      checks['rgc_inv_001'] = fail('rgc_inv_001', 'RGC-INV-001: tar_id missing');
    }

    // RGC-INV-002 — CES formula integrity
    const cesT = Number(rcr['ces_temporal']  ?? 0);
    const cesB = Number(rcr['ces_budget']    ?? 0);
    const cesD = Number(rcr['ces_context']   ?? 0);
    const cesI = Number(rcr['ces_integrity'] ?? 0);
    const storedCes     = rcr['ces_score'] != null ? Number(rcr['ces_score']) : -1;
    const recomputedCes = computeCes(cesT, cesB, cesD, cesI);

    const formulaNote = `CES = T(${cesT})×0.30 + B(${cesB})×0.30 + D(${cesD})×0.20 + I(${cesI})×0.20 = ${recomputedCes}`;
    if (storedCes < 0) {
      checks['ces_formula_rgc_inv_002'] = pass(`ces_score absent; recomputed: ${recomputedCes}`);
    } else if (Math.abs(storedCes - recomputedCes) <= CES_TOLERANCE) {
      checks['ces_formula_rgc_inv_002'] = pass(formulaNote);
      notes.push(`RGC-INV-002 PASS: ${formulaNote}`);
    } else {
      checks['ces_formula_rgc_inv_002'] = fail('ces_formula_rgc_inv_002',
        `RGC-INV-002 FAIL: stored=${storedCes} recomputed=${recomputedCes}. ${formulaNote}`);
    }

    // RGC-INV-003 — Status-CES consistency
    const effectiveCes    = storedCes >= 0 ? storedCes : recomputedCes;
    const expectedStatus  = cesScoreToStatus(effectiveCes);
    const storedStatusStr = String(rcr['continuity_status'] ?? '') as ContinuityStatus;
    const validStatuses: ContinuityStatus[] = ['NOMINAL','MONITORING','WARNING','CRITICAL','HALT'];

    if (!validStatuses.includes(storedStatusStr)) {
      checks['status_mismatch_rgc_inv_003'] = fail('status_mismatch_rgc_inv_003',
        `RGC-INV-003: unrecognised continuity_status: ${storedStatusStr}`);
    } else if (storedStatusStr === expectedStatus) {
      checks['status_mismatch_rgc_inv_003'] = pass(`${storedStatusStr} consistent with CES ${effectiveCes}`);
    } else {
      checks['status_mismatch_rgc_inv_003'] = fail('status_mismatch_rgc_inv_003',
        `RGC-INV-003 FAIL: stored=${storedStatusStr} expected=${expectedStatus} for CES=${effectiveCes}`);
    }

    // RGC-INV-004 — HALT requires escalation_event_id
    const isHalt        = storedStatusStr === 'HALT';
    const escId         = rcr['escalation_event_id'];
    const hasEscalation = escId != null && escId !== '' && escId !== null;
    if (isHalt && !hasEscalation) {
      checks['halt_no_escalation_rgc_inv_004'] = fail('halt_no_escalation_rgc_inv_004',
        'RGC-INV-004: HALT requires escalation_event_id');
    } else {
      checks['halt_no_escalation_rgc_inv_004'] = pass(
        isHalt ? 'RGC-INV-004: HALT + escalation_event_id present'
               : `RGC-INV-004: N/A (status=${storedStatusStr})`
      );
    }

    // ATF-INV-004 — Content hash (optional in RCR)
    const storedHash   = String(rcr['content_hash'] ?? '');
    const computedHash = computeContentHash(rcr);
    const isExample    = isExampleReceipt(rcr);
    if (isExample || !storedHash) {
      checks['content_hash_mismatch'] = pass(isExample ? 'SKIP (example)' : 'content_hash absent (optional)');
    } else if (storedHash === computedHash) {
      checks['content_hash_mismatch'] = pass(`content_hash verified: ${computedHash.slice(0,40)}...`);
    } else {
      checks['content_hash_mismatch'] = fail('content_hash_mismatch', `ATF-INV-004 FAIL in RCR ${rcrId}`);
    }

    return {
      receiptId: rcrId,
      receiptType: 'runtime_continuity_record',
      verdict: deriveVerdict(checks),
      checks,
      notes,
    };
  }
  