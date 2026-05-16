# ATF Protocol Porting Guide

Step-by-step guide for implementing a new language port of the ATF verifier.
After following this guide, your implementation will pass all 34 official
conformance vectors and be eligible to claim an ATF compliance profile.

> This guide is language-agnostic. Examples use pseudocode.
> For Rust specifics, see comments in `src/hash.rs` and `src/lib.rs`.

---

## Before you start

Read these sections (10 min total):
- RFC-ATF-1.md §5 — Delegation Receipt wire format
- RFC-ATF-2.md §5 — Runtime Continuity Record + CES formula
- CONFORMANCE.md — How conformance profiles work

The Python reference implementation is the source of truth for all
ambiguous cases: `verifier/verify_receipt.py` + `reference-implementation/`.

---

## Step 1 — Type definitions

Define types matching the ATF wire format exactly.
Key fields and their types:

| Field | Type | Notes |
|---|---|---|
| `delegation_id` | string | must match ATFDR-[0-9A-F]{16} |
| `authority_budget_granted` | float64 | MAR: must not exceed delegator |
| `authority_budget_delegator` | float64 | MAR reference value |
| `issued_at` / `expires_at` | ISO-8601 string | parse as UTC datetime |
| `execution_ns` | uint64 | nanoseconds — use integer, NOT float |
| `ces_score` | float64 | 0.0 to 100.0 |
| `continuity_status` | enum | NOMINAL/MONITORING/WARNING/CRITICAL/HALT |

**Critical:** `execution_ns` must be an integer type (u64 in Rust, bigint in TS).
Float64 cannot represent nanosecond Unix timestamps without precision loss.

## Step 2 — Normative reason codes

These string values are part of the protocol. They must match exactly
across all language implementations (FVP-INV-007).

| Invariant | Reason code |
|---|---|
| ATF-INV-001 | `mar_atf_inv_001` |
| ATF-INV-002 | `id_format_atf_inv_002` |
| ATF-INV-003 | `chain_root_atf_inv_003` |
| ATF-INV-004 | `content_hash_mismatch` |
| ATF-INV-006 (expired) | `expired_atf_inv_006` |
| ATF-INV-006 (inversion) | `temporal_inversion_atf_inv_006` |
| RGC-INV-001 | `rgc_inv_001` |
| RGC-INV-002 | `ces_formula_rgc_inv_002` |
| RGC-INV-003 | `status_mismatch_rgc_inv_003` |
| RGC-INV-004 | `halt_no_escalation_rgc_inv_004` |

## Step 3 — Content hash (the critical path)

Every other invariant check is independent. The content hash is not.
Every vector depends on it being correct.

**Python reference (your output must be identical):**

```python
EXCLUDE = {"content_hash", "pqc_signature", "pqc_algorithm", "_comment", "_ces_formula", "_test_note"}
payload  = {k: v for k, v in receipt.items() if k not in EXCLUDE}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
digest   = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
return f"sha256:{digest}"
```

**What this means:**
1. Remove excluded fields from the receipt object
2. Serialize with keys sorted lexicographically (ascending)
3. No whitespace: no space after comma or colon
4. Nested objects: also sort keys recursively
5. SHA-256 of the UTF-8 bytes
6. Return `"sha256:" + hex_digest`

**Verify parity before proceeding:**

```bash
python verifier/verify_receipt.py examples/delegation_receipt.json --verbose
# Note the "computed" hash in output
# Your implementation must return the same string
```

**Common pitfalls:**
- Key sorting must be recursive (nested objects too)
- `100.0` must serialize as `100.0`, not `100` — match Python behavior
- Arrays: preserve element order; only sort object keys
- `json.dumps(..., ensure_ascii=False)` means Unicode chars are literal, not escaped

## Step 4 — ATF-INV-001 (MAR)

```
if authority_budget_granted > authority_budget_delegator:
    return FAIL, reason_code="mar_atf_inv_001"
```

Edge case: `granted == delegator` is **VALID**.
Test: V-ATF-002-P uses equal budget and expects PASS.

## Step 5 — ATF-INV-002 (ID format)

```
pattern: ATFDR-[0-9A-F]{16}
         exactly 16 uppercase hex digits
         "ATFDR-" prefix is literal
```

If violated: FAIL with `id_format_atf_inv_002`.
Test: V-ATF-003-N uses `"INVALID-ID"` and expects FAIL.

## Step 6 — ATF-INV-003 (chain root)

For root DRs (`delegation_depth == 1`):
```
chain_root_id MUST equal delegation_id
```
If not: FAIL with `chain_root_atf_inv_003`.
Test: V-ATF-004-N has mismatched chain_root_id and expects FAIL.

## Step 7 — ATF-INV-006 (temporal validity)

Check in this order:
1. Parse `issued_at` and `expires_at` as RFC-3339 UTC timestamps
2. If `issued_at > expires_at`: FAIL with `temporal_inversion_atf_inv_006`
3. If `expires_at < now`: FAIL with `expired_atf_inv_006`
4. Otherwise: PASS

Test: V-ATF-006-N has an `expires_at` in 2020 (past), expects FAIL.
Test: V-ATF-007-N has `issued_at > expires_at`, expects FAIL.

## Step 8 — Checkpoint: run ATF vectors

```bash
cargo test atf_vectors   # Rust
pytest tests/test_conformance_vectors.py::TestATFCompliantProfile  # Python
npx jest --testNamePattern ATF  # TypeScript
```

All 15 V-ATF-* vectors should pass now.

## Step 9 — RGC-INV-001 (TAR presence)

```
if rcr.tar_id is None or rcr.tar_id == "":
    return FAIL, reason_code="rgc_inv_001"
```

## Step 10 — RGC-INV-002 (CES formula)

**Fixed weights — must not be configurable:**
```
CES = ces_temporal  * 0.30
    + ces_budget    * 0.30
    + ces_context   * 0.20
    + ces_integrity * 0.20
```

Validate:
- `|computed_ces - stored_ces_score| <= 0.01` (float tolerance)
- `stored_ces_score` is in `[0.0, 100.0]`

If either fails: FAIL with `ces_formula_rgc_inv_002`.

Test: V-RGC-002-N stores `ces_score=95.0` when components give `10.0`. Expects FAIL.

## Step 11 — RGC-INV-003 (status consistency)

**Thresholds (normative, must be exact):**
```
ces >= 75.0  ->  NOMINAL
ces >= 50.0  ->  MONITORING
ces >= 30.0  ->  WARNING
ces >= 10.0  ->  CRITICAL
ces <  10.0  ->  HALT
```

Derive expected status from `ces_score`. Compare with stored `continuity_status`.
If they differ: FAIL with `status_mismatch_rgc_inv_003`.

Test: V-RGC-004-N has `ces_score=5.0` with `continuity_status="NOMINAL"`. Expects FAIL.

## Step 12 — RGC-INV-004 (HALT escalation)

```
if continuity_status == "HALT" and escalation_event_id is None:
    return FAIL, reason_code="halt_no_escalation_rgc_inv_004"
```

Test: V-RGC-005-N has `continuity_status="HALT"` with `escalation_event_id=null`. Expects FAIL.

## Step 13 — Final check

```bash
cargo test              # All 34 vectors + determinism tests
cargo clippy            # No warnings
cargo build --release   # Clean build
```

Expected output:
```
test atf_vectors ... ok    (15 vectors)
test rgc_vectors ... ok    (11 vectors)
test fei_vectors ... ok    (8 vectors)
test hash_is_deterministic ... ok
test signature_excluded_from_hash ... ok

test result: ok. 5 passed; 0 failed
```

## Step 14 — Register your implementation

1. Update [IMPLEMENTATIONS.md](../../IMPLEMENTATIONS.md) with your port details
2. Link to your CI run as conformance evidence
3. Add the ATF-RGC-Compliant badge to your repo README
4. Open a Pull Request

## Getting help

Open a GitHub Issue with:
- The vector ID that is failing (`V-ATF-001-N`, etc.)
- Your computed hash vs. expected (if it is a hash issue)
- Your language and library versions

Response within 48 hours.

---

*OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*