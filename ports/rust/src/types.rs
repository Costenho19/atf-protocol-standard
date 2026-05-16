//! ATF Protocol Type Definitions
//! RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub type AtfVersion = String;
pub type ContentHash = String;

/// Normative reason codes — stable across ATF versions and implementations.
/// The string values MUST match exactly across all ports (FVP-INV-007).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ReasonCode {
    #[serde(rename = "mar_atf_inv_001")]          MarAtfInv001,
    #[serde(rename = "id_format_atf_inv_002")]    IdFormatAtfInv002,
    #[serde(rename = "chain_root_atf_inv_003")]   ChainRootAtfInv003,
    #[serde(rename = "content_hash_mismatch")]    ContentHashMismatch,
    #[serde(rename = "expired_atf_inv_006")]      ExpiredAtfInv006,
    #[serde(rename = "temporal_inversion_atf_inv_006")] TemporalInversionAtfInv006,
    #[serde(rename = "rgc_inv_001")]              RgcInv001,
    #[serde(rename = "ces_formula_rgc_inv_002")]  CesFormulaRgcInv002,
    #[serde(rename = "status_mismatch_rgc_inv_003")] StatusMismatchRgcInv003,
    #[serde(rename = "halt_no_escalation_rgc_inv_004")] HaltNoEscalationRgcInv004,
    #[serde(rename = "pqc_unavailable")]          PqcUnavailable,
    #[serde(rename = "missing_required_fields")]  MissingRequiredFields,
}

// ── Delegation Receipt (RFC-ATF-1 §5) ───────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DelegationReceipt {
    pub delegation_id: String,
    pub atf_version: AtfVersion,
    pub receipt_type: String,
    pub issuer_id: String,
    pub delegate_id: String,
    pub chain_root_id: String,
    pub delegation_depth: u32,
    pub authority_budget_delegator: f64,
    pub authority_budget_granted: f64,
    pub task_scope: HashMap<String, serde_json::Value>,
    pub issued_at: String,
    pub expires_at: String,
    pub content_hash: ContentHash,
    pub pqc_signature: String,
    pub pqc_algorithm: String,
    #[serde(flatten)]
    pub extra: HashMap<String, serde_json::Value>,
}

// ── Runtime Continuity Record (RFC-ATF-2 §5) ─────────────────────────────────

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ContinuityStatus {
    #[serde(rename = "NOMINAL")]    Nominal,
    #[serde(rename = "MONITORING")] Monitoring,
    #[serde(rename = "WARNING")]    Warning,
    #[serde(rename = "CRITICAL")]   Critical,
    #[serde(rename = "HALT")]       Halt,
}

impl std::fmt::Display for ContinuityStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Self::Nominal    => write!(f, "NOMINAL"),
            Self::Monitoring => write!(f, "MONITORING"),
            Self::Warning    => write!(f, "WARNING"),
            Self::Critical   => write!(f, "CRITICAL"),
            Self::Halt       => write!(f, "HALT"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeContinuityRecord {
    pub rcr_id: String,
    pub atf_version: AtfVersion,
    pub receipt_type: String,
    pub delegation_id: String,
    pub agent_id: String,
    pub chain_root_id: String,
    pub tar_id: Option<String>,
    /// Nanosecond-precision timestamp — u64 avoids float precision loss (RGC-INV-006)
    pub execution_ns: u64,
    pub ces_temporal: f64,
    pub ces_budget: f64,
    pub ces_context: f64,
    pub ces_integrity: f64,
    pub ces_score: f64,
    pub continuity_status: ContinuityStatus,
    pub budget_at_admission: f64,
    pub budget_remaining: f64,
    pub context_drift_pct: f64,
    pub escalation_event_id: Option<String>,
    pub content_hash: ContentHash,
    pub pqc_signature: String,
    pub pqc_algorithm: String,
    #[serde(flatten)]
    pub extra: HashMap<String, serde_json::Value>,
}

// ── Verification result types ─────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Verdict { Pass, Fail, Warn }

/// Per-check result — field names match TypeScript/Python ports (FVP-INV-007).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CheckResult {
    pub ok: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reason: Option<ReasonCode>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
}

impl CheckResult {
    pub fn pass(note: impl Into<String>) -> Self {
        Self { ok: true, reason: None, note: Some(note.into()) }
    }
    pub fn fail(rc: ReasonCode, note: impl Into<String>) -> Self {
        Self { ok: false, reason: Some(rc), note: Some(note.into()) }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReceiptVerificationResult {
    pub verdict: Verdict,
    pub receipt_id: String,
    pub receipt_type: String,
    pub checks: std::collections::HashMap<String, CheckResult>,
    pub notes: Vec<String>,
}

/// Alias used throughout lib.rs — matches Python/TypeScript API surface (FVP-INV-007).
pub type VerificationReport = ReceiptVerificationResult;

#[derive(Debug, Clone, Default)]
pub struct VerifyOptions {
    /// ML-DSA-65 public key base64. If None, PQC check is skipped.
    pub public_key_b64: Option<String>,
    /// Override "now" for temporal checks (useful in tests).
    pub now_override: Option<chrono::DateTime<chrono::Utc>>,
}
