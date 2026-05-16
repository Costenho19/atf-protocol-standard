/**
   * ATF Protocol Type Definitions — @atf-protocol/verifier
   * RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3
   *
   * All BigInt fields represent nanosecond-precision timestamps.
   * DO NOT use number for execution_ns — JavaScript number cannot represent
   * nanosecond Unix timestamps without precision loss. Use bigint.
   */

  // ── Shared ────────────────────────────────────────────────────────────────────

  export type ContentHash = `sha256:${string}`;
  export type ATFVersion = "1.0" | "2.0" | "3.0";
  export type PQCAlgorithm = "ML-DSA-65";

  /** Normative reason codes — stable across ATF versions */
  export const ReasonCode = {
    // ATF-INV-001
    MAR_VIOLATION:              "mar_atf_inv_001",
    // ATF-INV-002
    ID_FORMAT:                  "id_format_atf_inv_002",
    // ATF-INV-003
    CHAIN_ROOT:                 "chain_root_atf_inv_003",
    // ATF-INV-004
    CONTENT_HASH_MISMATCH:      "content_hash_mismatch",
    // ATF-INV-006
    EXPIRED:                    "expired_atf_inv_006",
    TEMPORAL_INVERSION:         "temporal_inversion_atf_inv_006",
    // RGC-INV-001
    TAR_NULL:                   "rgc_inv_001",
    // RGC-INV-002
    CES_FORMULA:                "ces_formula_rgc_inv_002",
    // RGC-INV-003
    STATUS_MISMATCH:            "status_mismatch_rgc_inv_003",
    // RGC-INV-004
    HALT_NO_ESCALATION:         "halt_no_escalation_rgc_inv_004",
    // FVP-INV-007
    NON_DETERMINISTIC_VERIFIER: "fvp_inv_007",
    // Structure
    MISSING_REQUIRED_FIELDS:    "missing_required_fields",
    PQC_UNAVAILABLE:            "pqc_unavailable",
    PQC_SIGNATURE_INVALID:      "pqc_signature_invalid",
  } as const;

  export type ReasonCode = typeof ReasonCode[keyof typeof ReasonCode];

  // ── Delegation Receipt (RFC-ATF-1) ────────────────────────────────────────────

  export interface DelegationReceipt {
    delegation_id: string;
    atf_version: ATFVersion;
    receipt_type: "delegation_receipt";
    issuer_id: string;
    delegate_id: string;
    chain_root_id: string;
    delegation_depth: number;
    authority_budget_delegator: number;
    authority_budget_granted: number;
    task_scope: Record<string, unknown>;
    issued_at: string;          // ISO-8601
    expires_at: string;         // ISO-8601
    content_hash: ContentHash;
    pqc_signature: string;      // base64 ML-DSA-65 signature
    pqc_algorithm: PQCAlgorithm;
    [key: string]: unknown;     // protocol-defined extension fields
  }

  // ── Runtime Continuity Record (RFC-ATF-2) ─────────────────────────────────────

  export type ContinuityStatus = "NOMINAL" | "MONITORING" | "WARNING" | "CRITICAL" | "HALT";

  export interface RuntimeContinuityRecord {
    rcr_id: string;
    atf_version: ATFVersion;
    receipt_type: "runtime_continuity_record";
    delegation_id: string;
    agent_id: string;
    chain_root_id: string;
    tar_id: string | null;
    execution_ns: bigint | number;  // prefer bigint for nanosecond precision
    ces_temporal: number;
    ces_budget: number;
    ces_context: number;
    ces_integrity: number;
    ces_score: number;
    continuity_status: ContinuityStatus;
    budget_at_admission: number;
    budget_remaining: number;
    context_drift_pct: number;
    escalation_event_id?: string | null;
    content_hash: ContentHash;
    pqc_signature: string;
    pqc_algorithm: PQCAlgorithm;
    [key: string]: unknown;
  }

  export type ATFReceipt = DelegationReceipt | RuntimeContinuityRecord;

  // ── Verification Results ───────────────────────────────────────────────────────

  export type Verdict = "PASS" | "FAIL" | "WARN";

  export interface CheckResult {
    ok: boolean;
    reasonCode?: ReasonCode | string;
    detail?: string;
  }

  export interface ReceiptVerificationResult {
    verdict: Verdict;
    receiptId: string;
    receiptType: string;
    checks: {
      contentHash: CheckResult;
      pqcSignature: CheckResult;
      marInvariant?: CheckResult;
      cesFormula?: CheckResult;
      statusConsistency?: CheckResult;
      temporalValidity?: CheckResult;
      idFormat?: CheckResult;
      chainRoot?: CheckResult;
      tarPresence?: CheckResult;
      haltEscalation?: CheckResult;
    };
    notes: string[];
  }

  export interface ChainVerificationResult {
    verdict: Verdict;
    chainRootId: string;
    length: number;
    receipts: ReceiptVerificationResult[];
    chainIntegrity: CheckResult;
    notes: string[];
  }

  // ── Verifier Options ──────────────────────────────────────────────────────────

  export interface VerifyOptions {
    /** ML-DSA-65 public key (base64). If omitted, PQC signature check is skipped. */
    publicKeyB64?: string;
    /** Override "now" for temporal validity checks (useful in testing). */
    now?: Date;
  }

  export interface VerifyRCROptions extends VerifyOptions {
    /** If true, recompute CES score from components and validate against stored value. Default: true */
    recomputeCes?: boolean;
  }
  