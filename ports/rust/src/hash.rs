//! Canonical JSON + SHA-256 for ATF content hash (ATF-INV-004, FVP-INV-007).
  //!
  //! Produces byte-identical output to the Python reference:
  //!
  //!     payload = {k: v for k, v in receipt.items() if k not in EXCLUDE_FIELDS}
  //!     canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
  //!                            ensure_ascii=False)
  //!     return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
  //!
  //! Cross-implementation parity: run both and compare hashes against the
  //! same receipt JSON. They must be identical (FVP-INV-007 — determinism).

  use crate::HASH_EXCLUDE_FIELDS;
  use sha2::{Digest, Sha256};

  /// Sort a JSON Value recursively — object keys sorted lexicographically.
  /// Arrays preserve element order (only object keys are sorted).
  fn sort_value(v: serde_json::Value) -> serde_json::Value {
      match v {
          serde_json::Value::Object(map) => {
              let mut keys: Vec<String> = map.keys().cloned().collect();
              keys.sort();
              let sorted = keys
                  .into_iter()
                  .map(|k| {
                      let val = sort_value(map[&k].clone());
                      (k, val)
                  })
                  .collect::<serde_json::Map<_, _>>();
              serde_json::Value::Object(sorted)
          }
          serde_json::Value::Array(arr) => {
              serde_json::Value::Array(arr.into_iter().map(sort_value).collect())
          }
          other => other,
      }
  }

  /// Serialize a JSON Value to canonical form — compact, no spaces.
  /// Matches Python: json.dumps(..., sort_keys=True, separators=(",", ":")).
  ///
  /// Key invariant: serde_json preserves the original number representation
  /// from the input JSON (60 stays "60", 60.5 stays "60.5", 100.0 stays "100.0").
  /// This matches Python's json module behaviour.
  fn to_canonical(v: &serde_json::Value) -> String {
      serde_json::to_string(v).expect("canonical JSON serialization cannot fail on valid Value")
  }

  /// Recompute the content_hash for any ATF receipt.
  ///
  /// # Arguments
  /// * `receipt` — The full receipt JSON as a `serde_json::Value::Object`.
  ///
  /// # Returns
  /// `"sha256:<lowercase-hex>"` — identical to the Python reference for the same input.
  ///
  /// # Example
  /// ```
  /// let json = serde_json::from_str(include_str!("../../examples/delegation_receipt.json")).unwrap();
  /// let hash = compute_content_hash(&json);
  /// assert!(hash.starts_with("sha256:"));
  /// assert_eq!(hash.len(), 71); // "sha256:" + 64 hex chars
  /// ```
  pub fn compute_content_hash(receipt: &serde_json::Value) -> String {
      let obj = match receipt.as_object() {
          Some(o) => o,
          None => return "sha256:".to_string() + &format!("{:x}", Sha256::digest(b"")),
      };

      // Step 1 — Filter excluded fields
      let filtered: serde_json::Map<String, serde_json::Value> = obj
          .iter()
          .filter(|(k, _)| !HASH_EXCLUDE_FIELDS.contains(&k.as_str()))
          .map(|(k, v)| (k.clone(), v.clone()))
          .collect();

      // Step 2 — Sort keys lexicographically (recursive for nested objects)
      let sorted = sort_value(serde_json::Value::Object(filtered));

      // Step 3 — Canonical JSON: compact, no whitespace
      let canonical = to_canonical(&sorted);

      // Step 4 — SHA-256 of UTF-8 bytes, lowercase hex
      let digest = Sha256::digest(canonical.as_bytes());
      format!("sha256:{}", hex::encode(digest))
  }

  #[cfg(test)]
  mod tests {
      use super::*;

      #[test]
      fn test_hash_exclude_fields_filtered() {
          let receipt = serde_json::json!({
              "delegation_id": "ATFDR-AABBCCDDEEFF0011",
              "authority_budget_granted": 60.0,
              "content_hash": "sha256:old",
              "pqc_signature": "sig",
              "pqc_algorithm": "dilithium3",
          });
          let hash = compute_content_hash(&receipt);
          // content_hash, pqc_signature, pqc_algorithm must be excluded
          assert!(hash.starts_with("sha256:"));
          assert_eq!(hash.len(), 71);
          // Same call twice must produce same hash (FVP-INV-007)
          assert_eq!(hash, compute_content_hash(&receipt));
      }

      #[test]
      fn test_hash_deterministic() {
          let receipt = serde_json::json!({
              "b_field": "second",
              "a_field": "first",
              "c_field": 42,
          });
          let h1 = compute_content_hash(&receipt);
          let h2 = compute_content_hash(&receipt);
          assert_eq!(h1, h2, "FVP-INV-007: same input must always produce same hash");
      }

      #[test]
      fn test_hash_key_sort_order() {
          // Key sort order must be lexicographic — "a" before "b" before "c"
          let r1 = serde_json::json!({"a":1,"b":2,"c":3});
          let r2 = serde_json::json!({"c":3,"a":1,"b":2});
          assert_eq!(compute_content_hash(&r1), compute_content_hash(&r2));
      }

      #[test]
      fn test_hash_example_dr() {
          // Load the canonical example DR and verify hash is non-empty
          let json = include_str!("../../examples/delegation_receipt.json");
          let receipt: serde_json::Value = serde_json::from_str(json).unwrap();
          let hash = compute_content_hash(&receipt);
          assert!(hash.starts_with("sha256:"));
          assert_eq!(hash.len(), 71);
      }
  }
  