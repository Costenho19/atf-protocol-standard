//! ATF Conformance Vector Tests — Rust port
//!
//! Loads the official 34 conformance vectors from
//! conformance/conformance_vectors.json and checks that this implementation
//! produces the expected verdict for each one.
//!
//! Run: cargo test
//!
//! Expected output when all invariants are implemented:
//!   test atf_vectors ... ok  (15 vectors)
//!   test rgc_vectors ... ok  (11 vectors)
//!   test fei_vectors ... ok  (8 vectors)
//!   test hash_is_deterministic ... ok
//!   test signature_excluded_from_hash ... ok
//!
//! When starting from the skeleton, most tests will fail with "not implemented".
//! Work through PORTING_GUIDE.md step by step.
//! The test output tells you exactly which invariant is failing.

use atf_verifier::types::*;
use atf_verifier::{verify_delegation_receipt, verify_runtime_continuity_record};
use serde::Deserialize;
use std::path::PathBuf;

#[derive(Debug, Deserialize)]
struct Expected { verdict: String }

#[derive(Debug, Deserialize)]
struct Vector {
    id: String,
    #[allow(dead_code)] profile: String,
    invariant: String,
    kind: String,
    description: String,
    input: serde_json::Value,
    expected: Expected,
}

#[derive(Debug, Deserialize)]
struct VectorsFile { vectors: Vec<Vector> }

fn load_vectors() -> Vec<Vector> {
    // Navigate from ports/rust/ to repo root, then conformance/
    let manifest = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let vectors_path = manifest
        .parent().unwrap()  // ports/
        .parent().unwrap()  // repo root
        .join("conformance/conformance_vectors.json");
    let raw = std::fs::read_to_string(&vectors_path)
        .unwrap_or_else(|e| panic!("Cannot read vectors at {}: {}", vectors_path.display(), e));
    let data: VectorsFile = serde_json::from_str(&raw)
        .expect("conformance_vectors.json parse error");
    data.vectors
}

fn run_vector(v: &Vector) -> ReceiptVerificationResult {
    let opts = VerifyOptions::default();
    match v.input.get("receipt_type").and_then(|t| t.as_str()) {
        Some("delegation_receipt") => {
            let dr: DelegationReceipt = serde_json::from_value(v.input.clone())
                .unwrap_or_else(|e| panic!("Vector {}: parse error: {}", v.id, e));
            verify_delegation_receipt(&dr, &opts)
        }
        Some("runtime_continuity_record") => {
            let rcr: RuntimeContinuityRecord = serde_json::from_value(v.input.clone())
                .unwrap_or_else(|e| panic!("Vector {}: parse error: {}", v.id, e));
            verify_runtime_continuity_record(&rcr, &opts)
        }
        other => panic!("Vector {}: unknown receipt_type {:?}", v.id, other),
    }
}

fn verdict_str(v: &Verdict) -> &'static str {
    match v { Verdict::Pass => "PASS", Verdict::Fail => "FAIL", Verdict::Warn => "WARN" }
}

// ── ATF-Compliant profile — 15 vectors ───────────────────────────────────────
// Implement verify_delegation_receipt() to make these pass.

#[test]
fn atf_vectors() {
    let all = load_vectors();
    let vectors: Vec<_> = all.iter().filter(|v| v.id.starts_with("V-ATF-")).collect();
    let (mut passed, mut failed) = (0usize, 0usize);

    for v in &vectors {
        let result = run_vector(v);
        let actual = verdict_str(&result.verdict);
        if actual == v.expected.verdict {
            passed += 1;
        } else {
            failed += 1;
            eprintln!(
                "  FAIL [{} {}] {} | expected={} got={}\n       notes={:?}",
                v.id, v.invariant, v.description,
                v.expected.verdict, actual, result.notes
            );
        }
    }
    assert_eq!(failed, 0, "ATF-Compliant: {}/{} passed", passed, vectors.len());
    println!("ATF-Compliant vectors: {}/{} PASS", passed, vectors.len());
}

// ── ATF-RGC-Compliant profile — 11 vectors ───────────────────────────────────
// Implement verify_runtime_continuity_record() to make these pass.

#[test]
fn rgc_vectors() {
    let all = load_vectors();
    let vectors: Vec<_> = all.iter().filter(|v| v.id.starts_with("V-RGC-")).collect();
    let (mut passed, mut failed) = (0usize, 0usize);

    for v in &vectors {
        let result = run_vector(v);
        let actual = verdict_str(&result.verdict);
        if actual == v.expected.verdict {
            passed += 1;
        } else {
            failed += 1;
            eprintln!(
                "  FAIL [{} {}] {} | expected={} got={}",
                v.id, v.invariant, v.description,
                v.expected.verdict, actual
            );
        }
    }
    assert_eq!(failed, 0, "ATF-RGC-Compliant: {}/{} passed", passed, vectors.len());
}

// ── ATF-FEI-Compliant profile — 8 vectors ─────────────────────────────────────

#[test]
fn fei_vectors() {
    let all = load_vectors();
    let vectors: Vec<_> = all.iter().filter(|v| v.id.starts_with("V-FEI-")).collect();
    let (mut passed, mut failed) = (0usize, 0usize);

    for v in &vectors {
        let result = run_vector(v);
        let actual = verdict_str(&result.verdict);
        if actual == v.expected.verdict { passed += 1; }
        else {
            failed += 1;
            eprintln!("  FAIL [{} {}] {}", v.id, v.invariant, v.description);
        }
    }
    assert_eq!(failed, 0, "ATF-FEI-Compliant: {}/{} passed", passed, vectors.len());
}

// ── FVP-INV-007: Determinism ───────────────────────────────────────────────────
// These tests run against the hash module directly.
// They will fail until compute_content_hash() is implemented.

#[test]
fn hash_is_deterministic() {
    use atf_verifier::compute_content_hash;
    let receipt = serde_json::json!({
        "delegation_id": "ATFDR-AABBCCDDEEFF0011",
        "atf_version": "1.0",
        "authority_budget_delegator": 100.0,
        "authority_budget_granted": 60.0,
        "content_hash": "sha256:placeholder",
        "pqc_signature": "illustrative",
        "pqc_algorithm": "ML-DSA-65"
    });
    let h1 = compute_content_hash(&receipt);
    let h2 = compute_content_hash(&receipt);
    assert_eq!(h1, h2, "FVP-INV-007: compute_content_hash must be deterministic");
    assert!(h1.starts_with("sha256:"), "Must return sha256: prefix");
}

#[test]
fn signature_excluded_from_hash() {
    use atf_verifier::compute_content_hash;
    let receipt = serde_json::json!({
        "delegation_id": "ATFDR-AABBCCDDEEFF0011",
        "authority_budget_delegator": 100.0,
        "authority_budget_granted": 60.0,
        "content_hash": "sha256:placeholder",
        "pqc_signature": "SIGNATURE_A",
        "pqc_algorithm": "ML-DSA-65"
    });
    let mut receipt2 = receipt.clone();
    receipt2["pqc_signature"] = serde_json::json!("COMPLETELY_DIFFERENT");
    assert_eq!(
        compute_content_hash(&receipt),
        compute_content_hash(&receipt2),
        "pqc_signature must be excluded from content hash (ATF-INV-004)"
    );
}

// ── Snapshot test: parity with Python reference ───────────────────────────────
// Uncomment and fill in the expected hash after running:
//   python verifier/verify_receipt.py examples/delegation_receipt.json --verbose

// #[test]
// fn content_hash_matches_python_reference() {
//     use atf_verifier::compute_content_hash;
//     let dr_json = include_str!("../../../examples/delegation_receipt.json");
//     let receipt: serde_json::Value = serde_json::from_str(dr_json).unwrap();
//     let hash = compute_content_hash(&receipt);
//     // Fill in the expected hash from the Python verifier output:
//     let expected = "sha256:<fill-in-from-python-output>";
//     assert_eq!(hash, expected, "Hash must match Python reference (FVP-INV-007)");
// }