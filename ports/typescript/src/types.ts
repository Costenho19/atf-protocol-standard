/**
   * ATF Protocol Type Definitions
   * RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3
   */

  /** Normative reason codes — must match exactly across all ATF ports (FVP-INV-007). */
  export type ReasonCode =
    | 'mar_atf_inv_001'
    | 'id_format_atf_inv_002'
    | 'chain_root_atf_inv_003'
    | 'content_hash_mismatch'
    | 'expired_atf_inv_006'
    | 'temporal_inversion_atf_inv_006'
    | 'rgc_inv_001'
    | 'ces_formula_rgc_inv_002'
    | 'status_mismatch_rgc_inv_003'
    | 'halt_no_escalation_rgc_inv_004'
    | 'pqc_unavailable'
    | 'missing_required_fields';

  export type Verdict = 'PASS' | 'FAIL';

  export type ContinuityStatus =
    | 'NOMINAL'
    | 'MONITORING'
    | 'WARNING'
    | 'CRITICAL'
    | 'HALT';

  export interface CheckResult {
    ok: boolean;
    reason?: ReasonCode;
    note?: string;
  }

  export interface VerificationReport {
    receiptId: string;
    receiptType: 'delegation_receipt' | 'runtime_continuity_record';
    verdict: Verdict;
    checks: Record<string, CheckResult>;
    notes: string[];
  }

  export interface VerifyOptions {
    /** Base64-encoded ML-DSA-65 public key for PQC signature verification. */
    publicKeyB64?: string;
    /** Override current time (for testing). */
    nowOverride?: Date;
  }

  /** RFC-ATF-1 §5 Delegation Receipt wire format. */
  export interface DelegationReceipt {
    delegation_id: string;
    delegator_id?: string;
    issuer_id?: string;
    delegate_id: string;
    task_scope: Record<string, unknown>;
    authority_budget_delegator: number;
    authority_budget_granted: number;
    chain_root_id?: string;
    parent_delegation_id?: string | null;
    delegation_depth?: number;
    expires_at?: string;
    created_at?: string;
    status?: string;
    content_hash: string;
    pqc_signature: string;
    pqc_algorithm: string;
    [key: string]: unknown;
  }

  /** RFC-ATF-2 §5 Runtime Continuity Record wire format. */
  export interface RuntimeContinuityRecord {
    rcr_id: string;
    tar_id: string;
    delegation_id: string;
    agent_id: string;
    chain_root_id?: string;
    execution_ns?: bigint | number;
    ces_score: number;
    ces_temporal: number;
    ces_budget: number;
    ces_context: number;
    ces_integrity: number;
    continuity_status: ContinuityStatus;
    predecessor_rcr_id?: string | null;
    escalation_event_id?: string | null;
    content_hash?: string;
    pqc_signature?: string;
    pqc_algorithm?: string;
    [key: string]: unknown;
  }
  