# ATF Verifier — Rust Port Skeleton

**Status: Skeleton — contributions welcome**

This is the official Rust skeleton for the
[ATF Protocol Standard](https://github.com/Costenho19/atf-protocol-standard)
offline verifier. Type definitions, test infrastructure, and conformance
harness are complete. The verification logic needs to be implemented.

[![ATF Protocol](https://img.shields.io/badge/ATF%20Protocol-RFC--ATF--1%2F2%2F3-blue?style=flat-square)](https://github.com/Costenho19/atf-protocol-standard)
[![Conformance Vectors](https://img.shields.io/badge/Conformance%20Vectors-34%20total-orange?style=flat-square)](../../conformance/conformance_vectors.json)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

---

## What is already done

| Component | File | Status |
|---|---|---|
| Type definitions | `src/types.rs` | Complete |
| Reason codes (all 40 invariants) | `src/types.rs` | Complete |
| CES threshold helper | `src/lib.rs` | Complete |
| Protocol constants | `src/lib.rs` | Complete |
| SHA-256 wrapper | `src/hash.rs` | Complete |
| CLI binary | `src/main.rs` | Complete |
| Conformance harness | `tests/conformance.rs` | Complete |
| 34 official test vectors | `../../conformance/` | Complete |

## What needs to be implemented

**Three functions. That is all.**

| Function | File | Invariants | Vectors |
|---|---|---|---|
| `compute_content_hash()` | `src/hash.rs` | ATF-INV-004, FVP-INV-007 | All 34 depend on this |
| `verify_delegation_receipt()` | `src/lib.rs` | ATF-INV-001, 002, 003, 006 | V-ATF-001 to V-ATF-015 |
| `verify_runtime_continuity_record()` | `src/lib.rs` | RGC-INV-001, 002, 003, 004 | V-RGC-001 to V-RGC-011 |

---

## Getting started

```bash
git clone https://github.com/Costenho19/atf-protocol-standard
cd atf-protocol-standard/ports/rust

# See what fails (expected: "not implemented" panics)
cargo test 2>&1 | head -40

# Build the CLI
cargo build
```

Then follow [PORTING_GUIDE.md](./PORTING_GUIDE.md) step by step.
Start with `compute_content_hash()` in `src/hash.rs` — every other
check depends on it.

---

## Implementation order (recommended)

1. `src/hash.rs` — `canonical_json_sorted()` + verify with unit tests in the same file
2. ATF-INV-001 (MAR) — simplest invariant, immediate feedback from V-ATF-001-N
3. ATF-INV-002 (ID format) — regex check
4. ATF-INV-003 (chain root) — equality check
5. ATF-INV-006 (temporal validity) — parse ISO-8601 timestamps
6. `cargo test atf_vectors` — all 15 V-ATF-* vectors should now pass
7. RGC-INV-001 (TAR presence)
8. RGC-INV-002 (CES formula)
9. RGC-INV-003 (status consistency)
10. RGC-INV-004 (HALT escalation)
11. `cargo test` — all 34 vectors should pass

---

## Claiming ATF-RGC-Compliant

When `cargo test` shows all 26 V-ATF-* and V-RGC-* vectors passing:

1. Open a PR updating [IMPLEMENTATIONS.md](../../IMPLEMENTATIONS.md)
2. Include your CI run URL
3. Add this badge to your repo:

```markdown
[![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-RFC--ATF--2-blue?style=flat-square)](https://github.com/Costenho19/atf-protocol-standard/releases/tag/v2.0.0)
```

---

## Cross-implementation parity

Your `compute_content_hash()` must produce identical output to the Python
reference for the same input. Verify with:

```bash
# Python reference output
cd ../.. && python verifier/verify_receipt.py examples/delegation_receipt.json --verbose

# Your Rust output
cd ports/rust && cargo run -- ../../examples/delegation_receipt.json
```

Both must show the same `content_hash` value (FVP-INV-007).

---

*OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*