# ATF Reference Implementation (Python)

  Minimal Python implementation of the Agent Trust Fabric protocol.
  Implements RFC-ATF-1 (Delegation Receipts) and RFC-ATF-2 (Runtime Continuity Records)
  with full invariant enforcement at creation time.

  ## Install

  ```bash
  cd reference-implementation
  pip install -e .
  # With PQC signing support:
  pip install -e ".[pqc]"
  ```

  ## Usage

  ### Create and verify a Delegation Receipt

  ```python
  from atf_core import create_delegation_receipt, verify_receipt

  dr = create_delegation_receipt(
      delegator_id="HUMAN-harold.nunes",
      delegate_id="AID-FINANCE-9B8C7D6E5F4A3B2C",
      task_scope={
          "action": "equity_order_execution",
          "domain": "FINANCE",
          "constraints": ["max_order_value_usd:50000"]
      },
      budget_granted=60.0,
      budget_delegator=100.0,
      expires_in_seconds=86400,
  )

  result = verify_receipt(dr)
  print(result["verdict"])   # PASS
  print(result["checks"])
  ```

  ### Create a Runtime Continuity Record

  ```python
  from atf_core import create_runtime_continuity_record

  rcr = create_runtime_continuity_record(
      tar_id="ATFTAR-1F2E3D4C5B6A7890",
      delegation_id="ATFDR-3A7F9B2C1D4E5F6A",
      agent_id="AID-FINANCE-9B8C7D6E5F4A3B2C",
      chain_root_id="ATFDR-3A7F9B2C1D4E5F6A",
      ces_temporal=99.31,
      ces_budget=100.0,
      ces_context=73.0,
      ces_integrity=100.0,
      budget_at_admission=60.0,
      budget_remaining=60.0,
      context_drift_pct=27.0,
      sample_reason="SCHEDULED",
  )
  print(rcr["ces_score"])         # 91.25 — computed from formula
  print(rcr["continuity_status"]) # NOMINAL
  ```

  ### ATF-INV-001 enforcement

  ```python
  # This raises ValueError — budget expansion is forbidden
  create_delegation_receipt(
      delegator_id="HUMAN-harold.nunes",
      delegate_id="AID-AGENT-X",
      task_scope={"action": "test"},
      budget_granted=110.0,   # EXCEEDS delegator budget
      budget_delegator=100.0,
  )
  # ValueError: ATF-INV-001 (MAR) VIOLATED: budget_granted (110.0) must not exceed budget_delegator (100.0)
  ```

  ## Invariants Enforced

  | Invariant | Description | Enforced in |
  |---|---|---|
  | ATF-INV-001 (MAR) | budget_granted ≤ budget_delegator | `create_delegation_receipt` |
  | ATF-INV-002 | delegation_id format: ATFDR-{16HEX} | `create_delegation_receipt` |
  | ATF-INV-003 | chain_root_id = delegation_id for root DRs | `create_delegation_receipt` |
  | RGC-INV-001 | tar_id MUST NOT be null | `create_runtime_continuity_record` |
  | RGC-INV-002 | CES = T×0.30+B×0.30+D×0.20+I×0.20 | `create_runtime_continuity_record` |
  | RGC-INV-003 | continuity_status derived from CES thresholds | `create_runtime_continuity_record` |

  ## CES Status Thresholds (RGC-INV-003)

  | CES Score | Status |
  |---|---|
  | ≥ 75.0 | NOMINAL |
  | 50.0 – 74.9 | MONITORING |
  | 30.0 – 49.9 | WARNING |
  | 10.0 – 29.9 | CRITICAL |
  | < 10.0 | HALT |

  ## License

  CC BY 4.0 — © 2026 OMNIX QUANTUM LTD
  