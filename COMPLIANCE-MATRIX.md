# ATF Protocol Compliance Matrix

  Full traceability from each invariant to its RFC section, JSON schema field, conformance test, and verifier command.

  **Legend:**
  - ✅ Covered — test exists, CI-verified
  - 🔶 Partial — covered in verifier but no dedicated test
  - ❌ Gap — not yet covered by automated tooling

  ---

  ## ATF-INV Family (RFC-ATF-1)

  | Invariant | Description | RFC §| Schema Field | Test ID | Verifier Check | CI Status |
  |---|---|---|---|---|---|---|
  | ATF-INV-001 | Monotonic Authority Reduction (MAR) | §5.3 | `authority_budget_granted ≤ authority_budget_delegator` | `TestMARInvariant::test_valid_dr_satisfies_mar` | `mar_atf_inv_001` | ✅ |
  | ATF-INV-001 | MAR violation detection | §5.3 | — | `TestMARInvariant::test_authority_expansion_violates_mar` | `mar_atf_inv_001` | ✅ |
  | ATF-INV-001 | MAR boundary (granted = delegator) | §5.3 | — | `TestMARInvariant::test_equal_budget_satisfies_mar` | — | ✅ |
  | ATF-INV-002 | Identifier format ATFDR-{16HEX} | §5.1 | `delegation_id` (pattern) | `TestIdentifierFormats::test_dr_id_format` | — | ✅ |
  | ATF-INV-003 | chain_root_id = delegation_id for root | §5.2 | `chain_root_id` | `TestIdentifierFormats::test_chain_root_id_in_dr` | — | ✅ |
  | ATF-INV-004 | PQC signature covers content_hash | §5.4 | `pqc_signature` | `TestContentHash::test_tampered_receipt_hash_differs` | `pqc_signature` | ✅ |
  | ATF-INV-005 | Offline verifiability (no platform) | §5.5 | — | verifier smoke test (CI) | All checks | ✅ |
  | ATF-INV-006 | DR valid at TAR admission timestamp | §6.2 | `expires_at` | 🔶 (verifier) | — | 🔶 |

  ---

  ## RGC-INV Family (RFC-ATF-2)

  | Invariant | Description | RFC §| Schema Field | Test ID | Verifier Check | CI Status |
  |---|---|---|---|---|---|---|
  | RGC-INV-001 | tar_id MUST NOT be null | §5.1 | `tar_id` | `TestMARInvariant::test_rcr_skips_mar_check` | `rgc_inv_001` | ✅ |
  | RGC-INV-002 | CES = T×0.30+B×0.30+D×0.20+I×0.20 | §5.3 | `ces_score` | `TestCESFormula::test_valid_rcr_satisfies_ces_formula` | `ces_formula_rgc_inv_002` | ✅ |
  | RGC-INV-002 | CES manipulation detection | §5.3 | — | `TestCESFormula::test_manipulated_ces_score_fails` | — | ✅ |
  | RGC-INV-002 | Fixed weights (non-negotiable) | §5.3 | — | `TestCESFormula::test_ces_formula_weights_are_fixed` | — | ✅ |
  | RGC-INV-003 | Status from CES thresholds | §5.4 | `continuity_status` | `TestCESFormula::test_halt_condition`, `test_nominal_threshold` | — | ✅ |
  | RGC-INV-004 | HALT propagates to child delegations | §6.1 | — | ❌ | — | ❌ |
  | RGC-INV-005 | AFG fragmentation ≤ limit | §7.2 | `fragmentation_score` | ❌ | — | ❌ |
  | RGC-INV-006 | execution_ns strictly increasing | §5.2 | `execution_ns` | ❌ | — | ❌ |
  | RGC-INV-007 | Escalation recorded before CRITICAL | §6.2 | `escalation_event_id` | ❌ | — | ❌ |
  | RGC-INV-008 | RC resolved before HALT avoidance | §7.1 | `reauth_challenge_id` | ❌ | — | ❌ |

  ---

  ## GPIL-INV Family (RFC-ATF-3)

  | Invariant | Description | RFC §| Test ID | CI Status |
  |---|---|---|---|---|
  | GPIL-INV-001 | Policy class MUST be one of 4 defined types | §4.2 | ❌ | ❌ |
  | GPIL-INV-002 | CRGC MUST be signed by both parties | §5.3 | ❌ | ❌ |
  | GPIL-INV-003 | Policy class mismatch MUST reject delegation | §6.1 | ❌ | ❌ |

  ---

  ## ELR-INV Family (RFC-ATF-3)

  | Invariant | Description | RFC §| Test ID | CI Status |
  |---|---|---|---|---|
  | ELR-INV-001 | Every ATF artifact MUST have a lifecycle tier | §5.1 | ❌ | ❌ |
  | ELR-INV-002 | HOT→WARM transition MUST be immutable | §6.2 | ❌ | ❌ |
  | ELR-INV-003 | WARM retention MUST be ≥90 days | §7.1 | ❌ | ❌ |
  | ELR-INV-004 | COLD retention MUST be ≥7 years | §7.2 | ❌ | ❌ |

  ---

  ## EAP-INV Family (RFC-ATF-3)

  | Invariant | Description | RFC §| Test ID | CI Status |
  |---|---|---|---|---|
  | EAP-INV-001 | Archive entries MUST be Merkle-chained | §5.2 | ❌ | ❌ |
  | EAP-INV-002 | ARH MUST be PQC-signed | §5.4 | ❌ | ❌ |
  | EAP-INV-003 | No entry removal from archive | §6.1 | ❌ | ❌ |
  | EAP-INV-004 | Merkle proof MUST be reproducible | §5.3 | ❌ | ❌ |
  | EAP-INV-005 | **Offline verifiability — no platform access** | §7.1 | Smoke test (CI) | ✅ |
  | EAP-INV-006 | Archive integrity cross-checkpoint | §6.3 | ❌ | ❌ |
  | EAP-INV-007 | Entry hash covers full receipt payload | §5.2 | `TestContentHash` | ✅ |

  ---

  ## OEP-INV Family (RFC-ATF-3)

  | Invariant | Description | RFC §| Test ID | CI Status |
  |---|---|---|---|---|
  | OEP-INV-001 | Package MUST be self-contained | §4.1 | ❌ | ❌ |
  | OEP-INV-002 | Manifest MUST include schema version | §4.2 | ❌ | ❌ |
  | OEP-INV-003 | Package MUST include issuer public key | §5.1 | ❌ | ❌ |
  | OEP-INV-004 | All receipts MUST have Merkle proofs | §5.2 | ❌ | ❌ |
  | OEP-INV-005 | Package integrity verified by ARH | §5.3 | ❌ | ❌ |
  | OEP-INV-006 | Manifest hash covers all package contents | §5.4 | ❌ | ❌ |

  ---

  ## FEA-INV Family (RFC-ATF-3)

  | Invariant | Description | RFC §| Test ID | CI Status |
  |---|---|---|---|---|
  | FEA-INV-001 | Export requires authentication | §4.1 | ❌ | ❌ |
  | FEA-INV-002 | Caller key MUST be registered | §4.2 | ❌ | ❌ |
  | FEA-INV-003 | Export receipt MUST be issued | §5.1 | ❌ | ❌ |
  | FEA-INV-004 | Export receipt MUST be PQC-signed | §5.2 | ❌ | ❌ |
  | FEA-INV-005 | Caller keys MUST NOT be self-provided in production | §6.1 | ❌ | ❌ |

  ---

  ## FVP-INV Family (RFC-ATF-3)

  | Invariant | Description | RFC §| Test ID | CI Status |
  |---|---|---|---|---|
  | FVP-INV-007 | Verifier determinism — same key+evidence = same result | §5.1 | `TestContentHash::test_compute_hash_is_deterministic` | ✅ |

  ---

  ## Coverage Summary

  | Family | Total | ✅ Covered | 🔶 Partial | ❌ Gap |
  |---|---|---|---|---|
  | ATF-INV | 6 | 5 | 1 | 0 |
  | RGC-INV | 8 | 3 | 0 | 5 |
  | GPIL-INV | 3 | 0 | 0 | 3 |
  | ELR-INV | 4 | 0 | 0 | 4 |
  | EAP-INV | 7 | 2 | 0 | 5 |
  | OEP-INV | 6 | 0 | 0 | 6 |
  | FEA-INV | 5 | 0 | 0 | 5 |
  | FVP-INV | 1 | 1 | 0 | 0 |
  | **TOTAL** | **40** | **11** | **1** | **28** |

  > Gaps are documented and tracked. RFC-ATF-3 invariants (L5) require a full Evidence Archive Pipeline implementation to cover — currently specified in RFC-ATF-3 and tracked for the reference implementation roadmap. See [CONTRIBUTING.md](./CONTRIBUTING.md) to contribute coverage.

  ---

  ## Running the Conformance Suite

  ```bash
  pip install pytest pypqc jsonschema
  pytest tests/ -v --tb=short
  ```

  CI results: [GitHub Actions](https://github.com/Costenho19/atf-protocol-standard/actions/workflows/ci.yml)

  ---

  *OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
  