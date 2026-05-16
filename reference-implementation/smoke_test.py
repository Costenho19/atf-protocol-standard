#!/usr/bin/env python3
  """Smoke test for the ATF Core reference implementation.
  Verifies create_delegation_receipt, create_runtime_continuity_record,
  and verify_receipt work end-to-end with the correct invariants enforced.
  """
  from atf_core import create_delegation_receipt, create_runtime_continuity_record, verify_receipt

  # Test 1: Create a valid DR and verify it passes
  dr = create_delegation_receipt(
      delegator_id='HUMAN-test',
      delegate_id='AID-TEST-AABBCCDDEEFF0011',
      task_scope={'action': 'test'},
      budget_granted=60.0,
      budget_delegator=100.0,
  )
  result = verify_receipt(dr)
  assert result['verdict'] == 'PASS', f"DR verify failed: {result}"
  print('DR create + verify: PASS')

  # Test 2: ATF-INV-001 (MAR) — budget_granted > budget_delegator must raise
  try:
      create_delegation_receipt(
          delegator_id='HUMAN-test',
          delegate_id='AID-TEST-AABBCCDDEEFF0011',
          task_scope={'action': 'test'},
          budget_granted=110.0,
          budget_delegator=100.0,
      )
      assert False, 'MAR violation should have raised ValueError'
  except ValueError as e:
      assert 'ATF-INV-001' in str(e), f"Expected ATF-INV-001 in error: {e}"
      print('ATF-INV-001 enforcement: PASS')

  # Test 3: Create a valid RCR (NOMINAL status)
  rcr = create_runtime_continuity_record(
      tar_id='ATFTAR-1F2E3D4C5B6A7890',
      delegation_id=dr['delegation_id'],
      agent_id='AID-TEST-AABBCCDDEEFF0011',
      chain_root_id=dr['chain_root_id'],
      ces_temporal=99.0,
      ces_budget=100.0,
      ces_context=80.0,
      ces_integrity=100.0,
      budget_at_admission=60.0,
      budget_remaining=60.0,
      context_drift_pct=20.0,
  )
  assert rcr['continuity_status'] == 'NOMINAL', f"Expected NOMINAL, got: {rcr['continuity_status']}"
  ces = rcr['ces_score']
  status = rcr['continuity_status']
  print(f'RCR: PASS — CES={ces} {status}')
  print('All smoke tests passed.')
  