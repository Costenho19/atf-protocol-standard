/**
   * CES (Continuity Evidence Score) formula and status mapping.
   * RFC-ATF-2 §5.3 — RGC-INV-001 / RGC-INV-003.
   *
   * IMPORTANT: The formula weights and status thresholds are normative
   * protocol constants. They MUST NOT be configurable or modified.
   */

  import type { ContinuityStatus } from './types';

  /** CES formula weights (RGC-INV-002 — immutable). */
  export const CES_WEIGHTS = {
    TEMPORAL:  0.30,
    BUDGET:    0.30,
    CONTEXT:   0.20,
    INTEGRITY: 0.20,
  } as const;

  /** Tolerance for f64 CES comparison. */
  export const CES_TOLERANCE = 0.01;

  /**
   * Compute CES score from its four components.
   * CES = T×0.30 + B×0.30 + D×0.20 + I×0.20
   *
   * This formula is a protocol invariant (RGC-INV-002).
   * It must not be extended or modified.
   */
  export function computeCes(
    temporal: number,
    budget: number,
    context: number,
    integrity: number,
  ): number {
    const raw =
      temporal  * CES_WEIGHTS.TEMPORAL  +
      budget    * CES_WEIGHTS.BUDGET    +
      context   * CES_WEIGHTS.CONTEXT   +
      integrity * CES_WEIGHTS.INTEGRITY;
    return Math.round(raw * 100) / 100;
  }

  /**
   * Map a CES score to a ContinuityStatus.
   * Thresholds are normative (RGC-INV-003) — not configurable.
   *
   * | CES        | Status     |
   * |------------|------------|
   * | ≥ 75.0     | NOMINAL    |
   * | ≥ 50.0     | MONITORING |
   * | ≥ 30.0     | WARNING    |
   * | ≥ 10.0     | CRITICAL   |
   * | < 10.0     | HALT       |
   */
  export function cesScoreToStatus(ces: number): ContinuityStatus {
    if (ces >= 75.0) return 'NOMINAL';
    if (ces >= 50.0) return 'MONITORING';
    if (ces >= 30.0) return 'WARNING';
    if (ces >= 10.0) return 'CRITICAL';
    return 'HALT';
  }
  