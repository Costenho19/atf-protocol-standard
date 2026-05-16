//! Canonical JSON + SHA-256 for ATF content hash (ATF-INV-004, FVP-INV-007).
//!
//! The algorithm must produce byte-identical output to the Python reference:
//!
//!     payload = {k: v for k, v in receipt.items() if k not in EXCLUDE_FIELDS}
//!     canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
//!                            ensure_ascii=False)
//!     return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
//!
//! Cross-implementation parity test:
//!   1. Take examples/delegation_receipt.json
//!   2. Run Python: python verifier/verify_receipt.py examples/delegation_receipt.json
//!   3. Note the computed hash
//!   4. Your compute_content_hash() must return the same string
//!
//! Known pitfalls:
//!   - serde_json::to_string() does NOT sort keys. You must sort manually.
//!   - f64 100.0 must serialize as "100.0", not "100" (match Python behavior).
//!   - Nested objects also need sorted keys (recursive sort).
//!   - Arrays: preserve element order, only sort object keys.

use crate::HASH_EXCLUDE_FIELDS;
use sha2::{Digest, Sha256};

/// Recompute the content_hash for an ATF receipt.
/// Returns "sha256:<hex>" (FVP-INV-007: same input always produces same output).
///
/// # TODO: implement this function
///
/// Steps:
///   1. Filter out HASH_EXCLUDE_FIELDS from the JSON object
///   2. Serialize remaining fields with keys sorted lexicographically
///      (no spaces: no space after "," or ":")
///   3. SHA-256 of the UTF-8 bytes
///   4. Return "sha256:" + hex(digest)
pub fn compute_content_hash(receipt: &serde_json::Value) -> String {
    let filtered = filter_hash_fields(receipt);
    let canonical = canonical_json_sorted(&filtered);
    let digest = sha256_hex(canonical.as_bytes());
    format!("sha256:{}", digest)
}

/// Remove HASH_EXCLUDE_FIELDS from a JSON object (top-level only).
fn filter_hash_fields(value: &serde_json::Value) -> serde_json::Value {
    match value {
        serde_json::Value::Object(map) => {
            let filtered: serde_json::Map<String, serde_json::Value> = map
                .iter()
                .filter(|(k, _)| !HASH_EXCLUDE_FIELDS.contains(&k.as_str()))
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect();
            serde_json::Value::Object(filtered)
        }
        other => other.clone(),
    }
}

/// Serialize a JSON value to canonical form:
///   - Object keys sorted lexicographically (ascending)
///   - No whitespace between tokens
///   - Recursive (nested objects also sorted)
///
/// # TODO: implement this function
///
/// The output must be identical to Python's:
///   json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
pub fn canonical_json_sorted(value: &serde_json::Value) -> String {
    // HINT: Match on Value variants:
    //   Value::Object(map) -> sort keys, recurse into values
    //   Value::Array(arr)  -> recurse into elements, preserve order
    //   Value::String(s)   -> format as JSON string (escape chars)
    //   Value::Number(n)   -> n.to_string() -- verify f64 format matches Python
    //   Value::Bool(b)     -> "true" or "false"
    //   Value::Null        -> "null"
    ///
    // For Object:
    //   let mut keys: Vec<&str> = map.keys().map(|s| s.as_str()).collect();
    //   keys.sort();  // lexicographic
    //   let pairs: Vec<String> = keys.iter().map(|k| {
    //       format!("{}:{}", json_escape_string(k), canonical_json_sorted(&map[*k]))
    //   }).collect();
    //   format!("{{{}}}", pairs.join(","))
    todo!("Implement canonical_json_sorted -- see docstring above")
}

/// Compute SHA-256 and return lowercase hex digest.
/// This is a thin wrapper around the sha2 crate.
pub fn sha256_hex(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hash_excludes_signature_fields() {
        // FVP-INV-007: changing pqc_signature must not change content_hash
        let mut receipt = serde_json::json!({
            "delegation_id": "ATFDR-AABBCCDDEEFF0011",
            "authority_budget_delegator": 100.0,
            "authority_budget_granted": 60.0,
            "content_hash": "sha256:placeholder",
            "pqc_signature": "SIGNATURE_A",
            "pqc_algorithm": "ML-DSA-65"
        });
        let h1 = compute_content_hash(&receipt);
        receipt["pqc_signature"] = serde_json::json!("COMPLETELY_DIFFERENT");
        let h2 = compute_content_hash(&receipt);
        assert_eq!(h1, h2, "pqc_signature must be excluded from content hash (ATF-INV-004)");
        assert!(h1.starts_with("sha256:"), "Must return sha256: prefix");
    }

    #[test]
    fn hash_is_deterministic() {
        // FVP-INV-007: same input always produces same output
        let receipt = serde_json::json!({
            "delegation_id": "ATFDR-AABBCCDDEEFF0011",
            "authority_budget_delegator": 100.0,
            "authority_budget_granted": 60.0
        });
        let h1 = compute_content_hash(&receipt);
        let h2 = compute_content_hash(&receipt);
        assert_eq!(h1, h2, "compute_content_hash must be deterministic (FVP-INV-007)");
    }

    #[test]
    fn hash_changes_on_field_modification() {
        // ATF-INV-004: any change to covered fields changes the hash
        let original = serde_json::json!({
            "delegation_id": "ATFDR-AABBCCDDEEFF0011",
            "authority_budget_granted": 60.0
        });
        let mut tampered = original.clone();
        tampered["authority_budget_granted"] = serde_json::json!(99.9);
        assert_ne!(
            compute_content_hash(&original),
            compute_content_hash(&tampered),
            "Modifying a covered field must change the hash (ATF-INV-004)"
        );
    }
}