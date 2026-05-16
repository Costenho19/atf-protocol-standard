//! atf-verifier — Rust port skeleton
//!
//! Offline verifier for Agent Trust Fabric receipts.
//! RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3 — zero platform dependency (EAP-INV-005).
//!
//! ## What needs to be implemented
//!
//! Three functions. That is it.
//! When all three are done, `cargo test` shows 34/34 conformance vectors passing.
//!
//! | Function | File | Invariants |
//! |---|---|---|
//! | `compute_content_hash()` | `src/hash.rs` | ATF-INV-004, FVP-INV-007 |
//! | `verify_delegation_receipt()` | `src/lib.rs` | ATF-INV-001, 002, 003, 006 |
//! | `verify_runtime_continuity_record()` | `src/lib.rs` | RGC-INV-001, 002, 003, 004 |
//!
//! Start with `compute_content_hash()` — every other check depends on it.
//! See PORTING_GUIDE.md for step-by-step instructions.

pub mod hash;
pub mod types;

pub use hash::compute_content_hash;
pub use types::*;

use std::collections::HashMap;
use types::*;

// ── Protocol constants (normative — do not change) ───────────────────────────

/// Fields excluded from content_hash computation (RFC-ATF-1 §5.2).
/// Changing this set is a protocol violation.
pub const HASH_EXCLUDE_FIELDS: &[&str] = &[
    "content_hash", "pqc_signature", "pqc_algorithm",
    "_comment", "_ces_formula", "_test_note",
];

/// CES formula weights — MUST NOT be configurable (RGC-INV-002).
pub const CES_WEIGHT_TEMPORAL:  f64 = 0.30;
pub const CES_WEIGHT_BUDGET:    f64 = 0.30;
pub const CES_WEIGHT_CONTEXT:   f64 = 0.20;
pub const CES_WEIGHT_INTEGRITY: f64 = 0.20;

/// Floating-point tolerance for CES comparison.
pub const CES_TOLERANCE: f64 = 0.01;

/// Delegation ID format: ATFDR-{16 uppercase hex digits} (ATF-INV-002).
pub const DR_ID_PATTERN: &str = r"^ATFDR-[0-9A-F]{16}$";

// ── Helpers (fully implemented — do not change) ───────────────────────────────

/// Convert CES score to ContinuityStatus per RFC-ATF-2 thresholds.
/// Thresholds are normative — do NOT modify (RGC-INV-003).
pub fn ces_score_to_status(ces: f64) -> ContinuityStatus {
    if      ces >= 75.0 { ContinuityStatus::Nominal }
    else if ces >= 50.0 { ContinuityStatus::Monitoring }
    else if ces >= 30.0 { ContinuityStatus::Warning }
    else if ces >= 10.0 { ContinuityStatus::Critical }
    else                { ContinuityStatus::Halt }
}

/// Derive overall verdict: any failing check -> FAIL, all pass -> PASS.
pub fn derive_verdict(checks: &HashMap<String, CheckResult>) -> Verdict {
    if checks.values().any(|c| !c.ok) { Verdict::Fail } else { Verdict::Pass }
}

// ── IMPLEMENT THIS ───────────────────────────────────────────────────────────
// verify_delegation_receipt
//
// Invariants to enforce:
//
//   ATF-INV-001  authority_budget_granted <= authority_budget_delegator
//   ATF-INV-002  delegation_id matches ATFDR-[0-9A-F]{16}
//   ATF-INV-003  chain_root_id == delegation_id  (for root DRs)
//   ATF-INV-004  compute_content_hash(receipt) == stored content_hash
//                (skip if stored == "sha256:placeholder")
//   ATF-INV-006  expires_at > now, issued_at <= expires_at
//
// When done, run: cargo test atf_vectors
// All 15 V-ATF-* vectors must pass.

pub fn verify_delegation_receipt(
    receipt: &DelegationReceipt,
    options: &VerifyOptions,
) -> ReceiptVerificationResult {
    let mut checks: HashMap<String, CheckResult> = HashMap::new();
    let mut notes: Vec<String> = Vec::new();

    // ── ATF-INV-004: content hash ────────────────────────────────────────────
    // TODO: serialize receipt to serde_json::Value, call compute_content_hash()
    // let receipt_value = serde_json::to_value(receipt).expect("serialize");
    // let computed = compute_content_hash(&receipt_value);
    // let hash_ok = receipt.content_hash == computed
    //               || receipt.content_hash == "sha256:placeholder";
    // checks.insert("content_hash", if hash_ok {
    //     CheckResult::pass(format!("computed={}", computed))
    // } else {
    //     notes.push("ATF-INV-004: content hash mismatch".into());
    //     CheckResult::fail(ReasonCode::ContentHashMismatch,
    //                       format!("stored={} computed={}", receipt.content_hash, computed))
    // });
    let _ = &receipt.content_hash; // suppress unused warning until implemented

    // ── ATF-INV-001: MAR ─────────────────────────────────────────────────────
    // TODO:
    // if receipt.authority_budget_granted > receipt.authority_budget_delegator {
    //     notes.push(format!("ATF-INV-001: granted {} > delegator {}",
    //                        receipt.authority_budget_granted,
    //                        receipt.authority_budget_delegator));
    //     checks.insert("mar_invariant",
    //         CheckResult::fail(ReasonCode::MarAtfInv001,
    //             format!("granted={} delegator={}",
    //                     receipt.authority_budget_granted,
    //                     receipt.authority_budget_delegator)));
    // } else {
    //     checks.insert("mar_invariant",
    //         CheckResult::pass(format!("granted={} <= delegator={}",
    //                                   receipt.authority_budget_granted,
    //                                   receipt.authority_budget_delegator)));
    // }

    // ── ATF-INV-002: ID format ───────────────────────────────────────────────
    // TODO: validate delegation_id against DR_ID_PATTERN
    // Hint: use the `regex` crate or a manual char-by-char check.

    // ── ATF-INV-003: chain root ──────────────────────────────────────────────
    // TODO: for root DRs (delegation_depth == 1),
    //       chain_root_id must equal delegation_id

    // ── ATF-INV-006: temporal validity ───────────────────────────────────────
    // TODO: parse issued_at and expires_at as chrono::DateTime<Utc>
    // let now = options.now.unwrap_or_else(chrono::Utc::now);
    // Check: issued_at > expires_at  -> temporal_inversion_atf_inv_006
    // Check: expires_at < now        -> expired_atf_inv_006
    let _ = &options.now;

    // ── ATF-INV-004 (cryptographic): PQC signature ───────────────────────────
    // TODO (optional, feature = "pqc"): verify ML-DSA-65 signature
    // Only if options.public_key_b64.is_some()

    let verdict = derive_verdict(&checks);
    ReceiptVerificationResult {
        verdict,
        receipt_id: receipt.delegation_id.clone(),
        receipt_type: "delegation_receipt".to_string(),
        checks,
        notes,
    }
}

// ── IMPLEMENT THIS ───────────────────────────────────────────────────────────
// verify_runtime_continuity_record
//
// Invariants to enforce:
//
//   RGC-INV-001  tar_id is Some and non-empty
//   RGC-INV-002  ces_score == T*0.30 + B*0.30 + D*0.20 + I*0.20  (±CES_TOLERANCE)
//                AND ces_score in [0.0, 100.0]
//   RGC-INV-003  continuity_status == ces_score_to_status(ces_score)
//   RGC-INV-004  if HALT: escalation_event_id is Some and non-empty
//
// When done, run: cargo test rgc_vectors
// All 11 V-RGC-* vectors must pass.

pub fn verify_runtime_continuity_record(
    rcr: &RuntimeContinuityRecord,
    options: &VerifyOptions,
) -> ReceiptVerificationResult {
    let mut checks: HashMap<String, CheckResult> = HashMap::new();
    let mut notes: Vec<String> = Vec::new();

    // ── RGC-INV-001: TAR presence ────────────────────────────────────────────
    // TODO:
    // let tar_ok = rcr.tar_id.as_deref().map(|s| !s.is_empty()).unwrap_or(false);
    // checks.insert("tar_presence", if tar_ok {
    //     CheckResult::pass(format!("tar_id={}", rcr.tar_id.as_deref().unwrap_or("")))
    // } else {
    //     notes.push("RGC-INV-001: tar_id must not be null".into());
    //     CheckResult::fail(ReasonCode::RgcInv001, "tar_id is null or empty")
    // });

    // ── RGC-INV-002: CES formula ─────────────────────────────────────────────
    // TODO:
    // let computed_ces = rcr.ces_temporal  * CES_WEIGHT_TEMPORAL
    //                  + rcr.ces_budget    * CES_WEIGHT_BUDGET
    //                  + rcr.ces_context   * CES_WEIGHT_CONTEXT
    //                  + rcr.ces_integrity * CES_WEIGHT_INTEGRITY;
    // let ces_in_range = rcr.ces_score >= 0.0 && rcr.ces_score <= 100.0;
    // let ces_ok = (computed_ces - rcr.ces_score).abs() <= CES_TOLERANCE && ces_in_range;

    // ── RGC-INV-003: status consistency ──────────────────────────────────────
    // TODO:
    // let expected_status = ces_score_to_status(rcr.ces_score);
    // let status_ok = rcr.continuity_status == expected_status;

    // ── RGC-INV-004: HALT requires escalation_event_id ───────────────────────
    // TODO:
    // if rcr.continuity_status == ContinuityStatus::Halt {
    //     let halt_ok = rcr.escalation_event_id
    //         .as_deref().map(|s| !s.is_empty()).unwrap_or(false);
    // }
    let _ = &options.public_key_b64;

    let verdict = derive_verdict(&checks);
    ReceiptVerificationResult {
        verdict,
        receipt_id: rcr.rcr_id.clone(),
        receipt_type: "runtime_continuity_record".to_string(),
        checks,
        notes,
    }
}