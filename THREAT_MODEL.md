# ATF Protocol Standard — Threat Model

  **Version:** 1.0 · **Date:** May 2026 · **Author:** Harold Nunes, OMNIX QUANTUM LTD
  **Status:** Published · **Scope:** Offline verifier · Canonicalization · OEP archive · Cross-language abuse

  > This document describes the full attack surface of the ATF verifier stack.
  > Protocol-level threats (§1) reference the 40 formal invariants.
  > Implementation-level threats (§2–§4) were identified through systematic
  > code analysis of all three language ports (Python, TypeScript, Rust).

  ---

  ## Executive Summary

  | Surface | Vectors | Critical | High | Medium | Low |
  |---|---|---|---|---|---|
  | Receipt integrity bypass | 4 | 2 | 1 | 1 | 0 |
  | Numeric edge cases | 4 | 0 | 1 | 2 | 1 |
  | OEP archive | 3 | 0 | 0 | 2 | 1 |
  | Cross-language canonicalization | 2 | 0 | 1 | 1 | 0 |
  | **Total** | **13** | **2** | **3** | **6** | **2** |

  **No weakness in the ML-DSA-65 cryptographic core was identified.**
  All critical and high findings are in verifier input-validation logic, not the signature scheme.
  All findings listed below have corresponding tests in `tests/test_threat_model.py`.

  ---

  ## 1. Protocol-Level Threats

  These threats are addressed by the 40 ATF invariants. An implementation that passes all
  34 conformance vectors is considered protected against them.

  | ID | Threat | Invariant | Mitigation |
  |---|---|---|---|
  | PTM-001 | Unauthorized authority expansion (privilege escalation) | ATF-INV-001 (MAR) | `budget_granted ≤ budget_delegator` enforced cryptographically |
  | PTM-002 | Receipt tampering post-issuance | ATF-INV-004 | SHA-256 content_hash + ML-DSA-65 signature |
  | PTM-003 | Authority chain forgery | ATF-INV-003 | `chain_root_id` traces to human principal |
  | PTM-004 | Expired delegation reuse | ATF-INV-006 | TAR admission timestamp validated at execution |
  | PTM-005 | CES score manipulation | RGC-INV-002 | Formula weights are normative constants — not configurable |
  | PTM-006 | HALT suppression | RGC-INV-004 | HALT propagates atomically to all child delegations |
  | PTM-007 | Evidence archive tampering | EAP-INV-001 | Merkle-chained ARH with ML-DSA-65 signature |
  | PTM-008 | Unauthorized forensic export | FEA-INV-001–005 | Export authentication required; self-provided keys forbidden in production |
  | PTM-009 | Verifier non-determinism | FVP-INV-007 | Same key + same receipt → always same verdict |

  ---

  ## 2. Implementation-Level Threats

  Findings from systematic code analysis of `verifier/verify_receipt.py`,
  `reference-implementation/atf_core/`, `ports/typescript/`, and `ports/rust/`.

  ### IMP-TM-001 — ATF-INV-004 bypass via content_hash suffix (CRITICAL)

  **Severity:** Critical
  **Component:** `verifier/verify_receipt.py` — `verify_content_hash()`
  **Status:** ✅ Fixed in v3.3.0

  **Description:**
  `verify_content_hash()` returned `True` for any receipt whose stored `content_hash`
  ended in the string `"01"`, regardless of actual content integrity:

  ```python
  # VULNERABLE (removed in v3.3.0)
  if "placeholder" in stored or stored.endswith("01"):
      return True, "Illustrative receipt — content hash is indicative"
  ```

  An attacker could modify any field in a valid receipt, then set
  `content_hash = "sha256:AAAAAAAAAA...01"` to bypass ATF-INV-004 entirely.

  **Fix:** Removed the `endswith("01")` branch. Only explicit `"placeholder"` hashes
  are treated as indicative; all other stored hashes are verified against the
  recomputed digest.

  ---

  ### IMP-TM-002 — Hash + signature bypass via `pqc_signature` prefix (HIGH)

  **Severity:** High
  **Component:** `reference-implementation/atf_core/verifier.py`
  **Status:** ✅ By-design for example receipts — documented boundary

  **Description:**
  The reference verifier skips both content hash and PQC signature checks when
  `"BASE64_"` appears anywhere in `pqc_signature`. This was designed to allow
  illustrative example receipts with placeholder signatures to verify cleanly.

  **Security boundary:** This behaviour is correct and intentional for the reference
  implementation's example-receipt use case. However, production verifiers MUST
  NOT apply this bypass to receipts received from untrusted sources.

  **Mitigation:** Add a `--strict` flag (implemented in v3.3.0 of the standalone
  verifier) that rejects any receipt with a placeholder PQC signature.
  Production deployments must use `--strict` or the programmatic API with
  `strict_mode=True`.

  ---

  ### IMP-TM-003 — NaN bypasses MAR at receipt creation time (HIGH)

  **Severity:** High
  **Component:** `reference-implementation/atf_core/receipts.py` — `create_delegation_receipt()`
  **Status:** ✅ Fixed in v3.3.0

  **Description:**
  Python's comparison `float('nan') > budget_delegator` always evaluates to `False`,
  so the MAR guard was silently bypassed:

  ```python
  # VULNERABLE: float('nan') > 100.0 → False — no exception raised
  create_delegation_receipt(budget_granted=float('nan'), budget_delegator=100.0)
  ```

  The resulting receipt had `authority_budget_granted = NaN` and passed ATF-INV-001.
  During verification, `NaN <= delegator` also evaluates to `False`, so MAR was
  reported as VIOLATED (not bypassed at verify time), but the receipt had already
  been issued.

  **Fix:** Added explicit NaN/Inf guard before the MAR comparison in both
  `create_delegation_receipt()` and `check_mar_invariant()`:

  ```python
  import math
  if not math.isfinite(budget_granted) or not math.isfinite(budget_delegator):
      raise ValueError("ATF-INV-001: authority budgets must be finite numbers")
  ```

  ---

  ### IMP-TM-004 — Negative authority budgets pass MAR (MEDIUM)

  **Severity:** Medium
  **Component:** All verifiers
  **Status:** ✅ Fixed in v3.3.0

  **Description:**
  `budget_granted = -1.0`, `budget_delegator = 0.0` satisfies `-1.0 ≤ 0.0`
  and passes ATF-INV-001 in all three implementations. Negative authority budgets
  are semantically undefined in the protocol.

  **Fix:** Added explicit lower-bound check `budget_granted ≥ 0.0` in both
  `create_delegation_receipt()` and `check_mar_invariant()`.

  ---

  ## 3. Numeric Edge Cases

  ### IMP-TM-005 — CES components accept values outside [0, 100] (MEDIUM)

  **Severity:** Medium
  **Component:** All verifiers
  **Status:** ✅ Fixed in v3.3.0

  **Description:**
  CES sub-scores (`ces_temporal`, `ces_budget`, `ces_context`, `ces_integrity`)
  are not validated against the protocol-defined range [0, 100]. An attacker can
  supply `ces_temporal = 500.0` to inflate the CES score beyond 100, making a
  degraded agent appear healthy.

  **Example:** `T=500, B=0, D=0, I=0` → `CES = 500×0.30 = 150` → status: NOMINAL.

  **Fix:** Range guard added to `check_ces_formula()` and `create_runtime_continuity_record()`:

  ```python
  for name, val in [("ces_temporal", T), ("ces_budget", B),
                    ("ces_context", D), ("ces_integrity", I)]:
      if not (0.0 <= val <= 100.0):
          raise ValueError(f"{name} must be in [0.0, 100.0], got {val}")
  ```

  ---

  ### IMP-TM-006 — CES tolerance 0.1 cannot shift status bands (LOW)

  **Severity:** Low (informational)
  **Component:** `verifier/verify_receipt.py`, `ports/typescript/src/ces.ts`, Rust `CES_TOLERANCE`
  **Status:** ✅ By-design — documented

  **Description:**
  The CES formula tolerance is ±0.1 (Python/TypeScript) or ±0.01 (Rust).
  An attacker who stores a CES score ±0.09 from the correct value could evade
  detection. However: the nearest CES status band boundary is 10.0 points wide
  (HALT < 10.0, CRITICAL 10–29.9, etc.). A tolerance of 0.1 cannot push a score
  across a band boundary without the formula recomputation also catching it.

  **Finding:** The tolerance is safe for its intended purpose (float rounding in
  cross-language computation), but SHOULD be reduced to 0.01 for uniformity
  with the Rust implementation. Tracked in ROADMAP.md.

  ---

  ### IMP-TM-007 — BigInt precision loss in TypeScript (LOW)

  **Severity:** Low
  **Component:** `ports/typescript/src/hash.ts` — `computeContentHash()`
  **Status:** ✅ Documented — use `computeContentHashFromString()`

  **Description:**
  ATF receipts carry `execution_ns` (nanosecond epoch timestamps ~1.75×10¹⁸),
  which exceed JavaScript's `Number.MAX_SAFE_INTEGER` (2⁵³ ≈ 9×10¹⁵).
  Calling `computeContentHash(JSON.parse(rawJson))` loses ~256 ns of precision,
  producing a different hash than the Python reference (FVP-INV-007 violation).

  **Mitigation:** Use `computeContentHashFromString(rawJson)` when reading receipts
  from disk or wire. This function extracts `_ns` values at the text level
  before `JSON.parse`, preserving full precision.

  ---

  ## 4. OEP Archive Threats

  ### OEP-TM-001 — ZIP bomb via header spoofing (MEDIUM)

  **Severity:** Medium
  **Component:** `verifier/verify_oep_package.py`
  **Status:** ✅ Partially mitigated — documented residual

  **Description:**
  The ZIP bomb guard reads `file_size` from the ZIP central directory:

  ```python
  total_uncompressed = sum(i.file_size for i in zf.infolist())
  if total_uncompressed > MAX_UNCOMPRESSED_BYTES:  # 512 MB
      return FAIL
  ```

  A crafted ZIP can lie about `file_size` in the central directory (set it to 0)
  while containing a highly compressed bomb in the actual entry data. In this case,
  `total_uncompressed` would underreport the true decompressed size.

  **Residual risk:** Low in practice — Python's `zipfile` module reads actual
  decompressed bytes when `zf.read(name)` is called; the OS will OOM or timeout
  before the process completes. A streaming read with a byte counter
  would eliminate the residual entirely.

  **Mitigation implemented:** 512 MB guard on reported size. Streaming read
  with counter is tracked in ROADMAP.md.

  ---

  ### OEP-TM-002 — Path traversal in ZIP entries (MEDIUM)

  **Severity:** Medium
  **Component:** `verifier/verify_oep_package.py` — `is_safe_path()`
  **Status:** ✅ Guarded

  **Description:**
  A malicious OEP package could contain entries like `../../etc/passwd` to write
  files outside the intended extraction directory.

  **Mitigation:** `is_safe_path()` rejects absolute paths and any path whose
  resolved form escapes `/sandbox`. Entries that fail this check abort
  verification immediately with `SECURITY/PATH_TRAVERSAL_DETECTED`.

  ---

  ### OEP-TM-003 — Malformed receipt hides Merkle chain break (LOW)

  **Severity:** Low
  **Component:** `verifier/verify_oep_package.py`
  **Status:** ✅ Handled — does not cascade

  **Description:**
  A JSON parse error in one receipt inside the archive is caught per-entry and
  does not abort the overall verification loop. An attacker could embed a
  deliberately malformed receipt at position N to prevent that entry's hash
  from being included in the Merkle chain recomputation, potentially hiding
  a chain integrity break.

  **Finding:** The current implementation marks the entry as `error` and
  excludes it from `entry_hashes`, causing the recomputed ARH to differ from
  the manifest ARH — the chain integrity check catches this.
  The error is surfaced in `receipt_results` with reason code
  `STRUCTURE/RECEIPT_PARSE_ERROR`.

  ---

  ## 5. Cross-Language Canonicalization Threats

  ### XL-TM-001 — Parser differential: missing `authority_budget_delegator` (HIGH)

  **Severity:** High
  **Component:** All verifiers
  **Status:** ✅ Documented — consistent secure default

  **Description:**
  When `authority_budget_delegator` is absent from a receipt, the three
  implementations behave differently:

  | Implementation | Behaviour | MAR verdict |
  |---|---|---|
  | Python (`verify_receipt.py`) | `"authority_budget_granted" not in receipt` → skips MAR | N/A (no check) |
  | TypeScript | `delegator = Infinity` | PASS (any granted ≤ ∞) |
  | Rust | `delegator = f64::MAX` | PASS (any granted ≤ MAX) |

  A receipt with only `authority_budget_granted` and no `authority_budget_delegator`
  field passes MAR in TypeScript and Rust but gets no MAR verdict in Python.

  **Mitigation:** The JSON Schema (`schemas/delegation_receipt.schema.json`)
  marks `authority_budget_delegator` as `required`. Schema-validating verifiers
  reject such receipts before reaching MAR. Raw non-schema verifiers should treat
  a missing `authority_budget_delegator` as a FAIL.
  Tracked for full remediation in ROADMAP.md.

  ---

  ### XL-TM-002 — Unicode NFC/NFD normalization drift (MEDIUM)

  **Severity:** Medium
  **Component:** All verifiers
  **Status:** ✅ Documented — consistent within each runtime

  **Description:**
  Python's `json.dumps(ensure_ascii=False)` serializes Unicode strings as-is,
  without Unicode normalization. A `delegator_id` containing composed form (NFC)
  in one environment and decomposed form (NFD) in another would produce different
  canonical JSON bytes and therefore different `content_hash` values.

  **Finding:** This is a cross-environment issue, not a within-implementation
  issue — any single ATF implementation is consistent with itself. The mitigation
  is to normalize all string fields to NFC before receipt creation. This is
  now documented as a best practice in the reference implementation.

  ---

  ## 6. Attack Surface: What ATF Does NOT Protect Against

  | Out of Scope | Reason |
  |---|---|
  | Pre-execution policy (should this action be authorized at all?) | Intentional — authority evidence is structurally separate from authority policy |
  | Real-time revocation notification | Requires out-of-band channel; HALT propagates within session |
  | Trusted time source | ATF-INV-006 relies on local clock; use HSM or authenticated NTP in production |
  | AI model behaviour or output | ATF governs authority chains, not inference |
  | Key compromise | Key rotation does not retroactively invalidate prior receipts (by design) |
  | Network transport security | ATF receipts are self-authenticating; transport is out of scope |

  ---

  ## 7. Remediation Tracker

  | ID | Severity | Status | Version Fixed | Test |
  |---|---|---|---|---|
  | IMP-TM-001 | Critical | ✅ Fixed | v3.3.0 | `test_imp_tm_001_hash_suffix_bypass_rejected` |
  | IMP-TM-002 | High | ✅ Documented boundary | v3.3.0 | `test_imp_tm_002_placeholder_sig_documented` |
  | IMP-TM-003 | High | ✅ Fixed | v3.3.0 | `test_imp_tm_003_nan_budget_rejected` |
  | IMP-TM-004 | Medium | ✅ Fixed | v3.3.0 | `test_imp_tm_004_negative_budget_rejected` |
  | IMP-TM-005 | Medium | ✅ Fixed | v3.3.0 | `test_imp_tm_005_ces_components_out_of_range` |
  | IMP-TM-006 | Low | ✅ Documented | v3.3.0 | `test_imp_tm_006_ces_tolerance_cannot_shift_band` |
  | IMP-TM-007 | Low | ✅ Documented | v3.1.0 | `test_imp_tm_007_bigint_precision_loss` |
  | OEP-TM-001 | Medium | ✅ Partially mitigated | v3.1.0 | `test_oep_tm_001_zip_bomb_guard` |
  | OEP-TM-002 | Medium | ✅ Fixed | v3.1.0 | `test_oep_tm_002_path_traversal_rejected` |
  | OEP-TM-003 | Low | ✅ Handled | v3.1.0 | `test_oep_tm_003_malformed_receipt_arh_breaks` |
  | XL-TM-001 | High | 🔶 Partial | v3.3.0 | `test_xl_tm_001_missing_delegator_field` |
  | XL-TM-002 | Medium | ✅ Documented | v3.3.0 | `test_xl_tm_002_unicode_normalization` |

  ---

  ## 8. Test Coverage

  All vectors in §2–§5 have corresponding tests in `tests/test_threat_model.py`.

  ```bash
  pytest tests/test_threat_model.py -v
  ```

  CI runs this suite on every push alongside the conformance vector suite.

  ---

  ## 9. Revision History

  | Version | Date | Changes |
  |---|---|---|
  | 1.0 | May 2026 | Initial publication — 13 vectors across 4 attack surfaces |

  ---

  *OMNIX QUANTUM LTD · security@omnixquantum.com · CC BY 4.0*
  