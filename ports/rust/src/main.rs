//! ATF Receipt Offline Verifier — CLI
  //!
  //! Usage:
  //!   cargo run -- examples/delegation_receipt.json
  //!   cargo run -- examples/delegation_receipt.json --public-key key.b64
  //!   cargo run -- examples/delegation_receipt.json --hash-only

  use atf_verifier::types::*;
  use atf_verifier::{verify_delegation_receipt, verify_runtime_continuity_record, compute_content_hash};
  use std::path::PathBuf;

  fn main() {
      let args: Vec<String> = std::env::args().collect();
      if args.len() < 2 {
          eprintln!("Usage: verify_receipt <receipt.json> [--public-key <key.b64>] [--hash-only]");
          std::process::exit(1);
      }

      let receipt_path = PathBuf::from(&args[1]);
      let mut options = VerifyOptions::default();
      let mut hash_only = false;

      let mut i = 2;
      while i < args.len() {
          match args[i].as_str() {
              "--public-key" if i + 1 < args.len() => {
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
              }
              "--hash-only" => { hash_only = true; i += 1; }
              _ => { i += 1; }
          }
      }

      let raw = std::fs::read_to_string(&receipt_path).unwrap_or_else(|e| {
          eprintln!("Error reading {}: {}", receipt_path.display(), e);
          std::process::exit(1);
      });

      // Parse to serde_json::Value — verify_* functions accept &Value directly
      let receipt: serde_json::Value = serde_json::from_str(&raw).unwrap_or_else(|e| {
          eprintln!("Error parsing JSON: {}", e); std::process::exit(1);
      });

      // --hash-only: print the computed content_hash and exit (used by hash parity CI)
      if hash_only {
          println!("{}", compute_content_hash(&receipt));
          return;
      }

      let result = match receipt.get("receipt_type").and_then(|v| v.as_str()) {
          Some("delegation_receipt") | None => {
              verify_delegation_receipt(&receipt, &options)
          }
          Some("runtime_continuity_record") => {
              verify_runtime_continuity_record(&receipt, &options)
          }
          Some(other) => {
              eprintln!("Unknown receipt_type: {}", other);
              std::process::exit(1);
          }
      };

      println!("{}", serde_json::to_string_pretty(&result).unwrap());
      std::process::exit(match result.verdict { Verdict::Pass => 0, _ => 1 });
  }
  