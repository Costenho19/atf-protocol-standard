//! ATF Receipt Offline Verifier — CLI
//!
//! Usage:
//!   cargo run -- examples/delegation_receipt.json
//!   cargo run -- examples/runtime_continuity_record.json --public-key key.b64
//!
//! Build release binary:
//!   cargo build --release
//!   ./target/release/verify_receipt examples/delegation_receipt.json

use atf_verifier::types::*;
use atf_verifier::{verify_delegation_receipt, verify_runtime_continuity_record};
use std::path::PathBuf;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: verify_receipt <receipt.json> [--public-key <key.b64>]");
        std::process::exit(1);
    }

    let receipt_path = PathBuf::from(&args[1]);
    let mut options = VerifyOptions::default();

    // Parse --public-key argument
    let mut i = 2;
    while i < args.len() {
        if args[i] == "--public-key" && i + 1 < args.len() {
            let key_path = PathBuf::from(&args[i + 1]);
            let key = if key_path.exists() {
                std::fs::read_to_string(&key_path).unwrap_or_else(|e| {
                    eprintln!("Error reading key: {}", e); std::process::exit(1);
                })
            } else {
                args[i + 1].clone()
            };
            options.public_key_b64 = Some(key.trim().to_string());
            i += 2;
        } else {
            i += 1;
        }
    }

    let raw = std::fs::read_to_string(&receipt_path).unwrap_or_else(|e| {
        eprintln!("Error reading {}: {}", receipt_path.display(), e);
        std::process::exit(1);
    });
    let receipt: serde_json::Value = serde_json::from_str(&raw).unwrap_or_else(|e| {
        eprintln!("Error parsing JSON: {}", e); std::process::exit(1);
    });

    let result = match receipt.get("receipt_type").and_then(|v| v.as_str()) {
        Some("delegation_receipt") => {
            let dr: DelegationReceipt = serde_json::from_value(receipt).unwrap_or_else(|e| {
                eprintln!("Parse error: {}", e); std::process::exit(1);
            });
            verify_delegation_receipt(&dr, &options)
        }
        Some("runtime_continuity_record") => {
            let rcr: RuntimeContinuityRecord = serde_json::from_value(receipt)
                .unwrap_or_else(|e| { eprintln!("Parse error: {}", e); std::process::exit(1); });
            verify_runtime_continuity_record(&rcr, &options)
        }
        other => {
            eprintln!("Unknown receipt_type: {:?}", other);
            std::process::exit(1);
        }
    };

    println!("{}", serde_json::to_string_pretty(&result).unwrap());
    std::process::exit(match result.verdict { Verdict::Pass => 0, _ => 1 });
}