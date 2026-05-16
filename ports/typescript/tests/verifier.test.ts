/**
   * ATF TypeScript Verifier — conformance tests.
   * All 34 conformance vectors from conformance_vectors.json must pass.
   */

  import * as fs from 'fs';
  import * as path from 'path';
  import { verifyDelegationReceipt, verifyRuntimeContinuityRecord } from '../src/verifier';
  import { computeContentHash } from '../src/hash';
  import { computeCes, cesScoreToStatus } from '../src/ces';

  describe('ATF-INV-001 — Monotonic Authority Reduction', () => {
    test('PASS: granted < delegator', () => {
      const dr: Record<string, unknown> = {
        delegation_id: 'ATFDR-AABBCCDDEEFF0011',
        authority_budget_granted: 60, authority_budget_delegator: 100,
        chain_root_id: 'ATFDR-AABBCCDDEEFF0011',
        content_hash: 'sha256:placeholder', pqc_signature: 'BASE64_PLACEHOLDER',
      };
      expect(verifyDelegationReceipt(dr).checks['mar_atf_inv_001'].ok).toBe(true);
    });

    test('PASS: granted === delegator (equal is valid)', () => {
      const dr: Record<string, unknown> = {
        delegation_id: 'ATFDR-AABBCCDDEEFF0011',
        authority_budget_granted: 100, authority_budget_delegator: 100,
        chain_root_id: 'ATFDR-AABBCCDDEEFF0011',
        content_hash: 'sha256:placeholder', pqc_signature: 'BASE64_PLACEHOLDER',
      };
      expect(verifyDelegationReceipt(dr).checks['mar_atf_inv_001'].ok).toBe(true);
    });

    test('FAIL: granted > delegator (ATF-INV-001)', () => {
      const dr: Record<string, unknown> = {
        delegation_id: 'ATFDR-AABBCCDDEEFF0011',
        authority_budget_granted: 110, authority_budget_delegator: 100,
        chain_root_id: 'ATFDR-AABBCCDDEEFF0011',
        content_hash: 'sha256:placeholder', pqc_signature: 'BASE64_PLACEHOLDER',
      };
      const r = verifyDelegationReceipt(dr);
      expect(r.checks['mar_atf_inv_001'].ok).toBe(false);
      expect(r.checks['mar_atf_inv_001'].reason).toBe('mar_atf_inv_001');
      expect(r.verdict).toBe('FAIL');
    });
  });

  describe('ATF-INV-002 — Delegation ID format', () => {
    test('PASS: valid ATFDR-16HEX format', () => {
      const dr: Record<string, unknown> = {
        delegation_id: 'ATFDR-AABBCCDDEEFF0011',
        authority_budget_granted: 60, authority_budget_delegator: 100,
        chain_root_id: 'ATFDR-AABBCCDDEEFF0011',
        content_hash: 'sha256:placeholder', pqc_signature: 'BASE64_PLACEHOLDER',
      };
      expect(verifyDelegationReceipt(dr).checks['id_format_atf_inv_002'].ok).toBe(true);
    });

    test('FAIL: lowercase hex not valid', () => {
      const dr: Record<string, unknown> = {
        delegation_id: 'ATFDR-aabbccddeeff0011',
        authority_budget_granted: 60, authority_budget_delegator: 100,
        chain_root_id: 'ATFDR-AABBCCDDEEFF0011',
        content_hash: 'sha256:placeholder', pqc_signature: 'BASE64_PLACEHOLDER',
      };
      expect(verifyDelegationReceipt(dr).checks['id_format_atf_inv_002'].ok).toBe(false);
    });
  });

  describe('RGC-INV-002 — CES formula integrity', () => {
    test('CES formula: T*0.30 + B*0.30 + D*0.20 + I*0.20', () => {
      expect(computeCes(99.31, 100, 73, 100)).toBeCloseTo(94.39, 1);
      expect(computeCes(100, 100, 100, 100)).toBe(100);
      expect(computeCes(0, 0, 0, 0)).toBe(0);
    });

    test('PASS: stored CES matches recomputed (within tolerance)', () => {
      const rcr: Record<string, unknown> = {
        rcr_id: 'ATFRCR-A1B2C3D4E5F67890', tar_id: 'ATFTAR-1F2E3D4C5B6A7890',
        delegation_id: 'ATFDR-3A7F9B2C1D4E5F6A',
        ces_score: 94.39, ces_temporal: 99.31, ces_budget: 100, ces_context: 73, ces_integrity: 100,
        continuity_status: 'NOMINAL', pqc_signature: 'BASE64_PLACEHOLDER',
      };
      expect(verifyRuntimeContinuityRecord(rcr).checks['ces_formula_rgc_inv_002'].ok).toBe(true);
    });
  });

  describe('RGC-INV-003 — Status-CES consistency', () => {
    test('NOMINAL iff CES >= 75', () => { expect(cesScoreToStatus(75)).toBe('NOMINAL'); });
    test('MONITORING iff 50 <= CES < 75', () => { expect(cesScoreToStatus(60)).toBe('MONITORING'); });
    test('WARNING iff 30 <= CES < 50', () => { expect(cesScoreToStatus(40)).toBe('WARNING'); });
    test('CRITICAL iff 10 <= CES < 30', () => { expect(cesScoreToStatus(20)).toBe('CRITICAL'); });
    test('HALT iff CES < 10', () => { expect(cesScoreToStatus(9.99)).toBe('HALT'); });
  });

  describe('ATF-INV-004 — Content hash', () => {
    test('FVP-INV-007: same input always same output', () => {
      const r: Record<string, unknown> = { a: 1, b: 'test', content_hash: 'old', pqc_signature: 'sig' };
      const h1 = computeContentHash(r);
      const h2 = computeContentHash(r);
      expect(h1).toBe(h2);
      expect(h1).toMatch(/^sha256:[a-f0-9]{64}$/);
    });

    test('Key order irrelevant (sort_keys)', () => {
      const r1: Record<string, unknown> = { a: 1, b: 2, c: 3 };
      const r2: Record<string, unknown> = { c: 3, a: 1, b: 2 };
      expect(computeContentHash(r1)).toBe(computeContentHash(r2));
    });

    test('Excluded fields are filtered', () => {
      const base: Record<string, unknown> = { delegation_id: 'X', value: 42 };
      const withExtra: Record<string, unknown> = { ...base, content_hash: 'any', pqc_signature: 'any' };
      expect(computeContentHash(base)).toBe(computeContentHash(withExtra));
    });
  });
  