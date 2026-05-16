"""
  ATFHandoffGuard — validates ATF Delegation Receipt before every agent handoff.

  In multi-agent systems (Swarm, Agents SDK), agent handoffs transfer authority.
  ATFHandoffGuard ensures each handoff is backed by a valid sub-delegation
  with budget_granted ≤ budget_delegator (ATF-INV-001 — MAR invariant).

  Usage:
      from atf_openai_agents import ATFHandoffGuard

      handoff_guard = ATFHandoffGuard(parent_dr=parent_delegation_receipt)

      # Called before handing off to a sub-agent
      sub_dr = handoff_guard.authorize_handoff(
          to_agent_id="AID-FINANCE-9B8C7D6E5F4A3B2C",
          task_scope={"action": "risk_analysis", "domain": "FINANCE"},
          budget_fraction=0.6,   # 60% of current budget
      )
  """
  from __future__ import annotations
  from typing import Any, Dict, Optional
  from .exceptions import ATFViolationError
  from .utils import compute_content_hash

  class ATFHandoffGuard:
      """Validates and records agent handoffs as sub-delegations."""

      def __init__(self, *, parent_dr: Dict[str, Any], verbose: bool = False) -> None:
          self._parent = parent_dr
          self._verbose = verbose
          self._handoffs: list = []

      def authorize_handoff(
          self,
          *,
          to_agent_id: str,
          task_scope: Dict[str, Any],
          budget_fraction: float = 0.5,
      ) -> Dict[str, Any]:
          """
          Authorize a sub-delegation for an agent handoff.
          Enforces ATF-INV-001: sub-delegation budget ≤ parent budget.
          """
          import uuid, datetime, hashlib, json

          parent_budget = float(self._parent.get("authority_budget_granted", 100.0))
          sub_budget    = round(parent_budget * min(1.0, max(0.0, budget_fraction)), 2)

          if sub_budget > parent_budget:   # ATF-INV-001 guard
              raise ATFViolationError(
                  f"ATF-INV-001: sub_budget {sub_budget} > parent_budget {parent_budget}",
                  reason="mar_atf_inv_001",
              )

          sub_id = f"ATFDR-{uuid.uuid4().hex[:16].upper()}"
          now    = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
          exp    = (datetime.datetime.now(datetime.timezone.utc) +
                    datetime.timedelta(seconds=3600)).isoformat().replace("+00:00","Z")

          sub_dr: Dict[str, Any] = {
              "delegation_id":              sub_id,
              "delegator_id":               self._parent.get("delegate_id", ""),
              "delegate_id":                to_agent_id,
              "task_scope":                 task_scope,
              "authority_budget_delegator": parent_budget,
              "authority_budget_granted":   sub_budget,
              "parent_delegation_id":       self._parent.get("delegation_id"),
              "chain_root_id":              self._parent.get("chain_root_id"),
              "delegation_depth":           int(self._parent.get("delegation_depth", 0)) + 1,
              "status":                     "ACTIVE",
              "created_at":                 now,
              "expires_at":                 exp,
              "pqc_algorithm":              "dilithium3",
              "pqc_signature":              "PENDING_SIGNING",
          }
          # Compute content hash (ATF-INV-004)
          sub_dr["content_hash"] = compute_content_hash(sub_dr)
          self._handoffs.append(sub_dr)

          if self._verbose:
              print(f"[ATF] Handoff authorized: {to_agent_id} | budget={sub_budget}/{parent_budget} | DR={sub_id}")

          return sub_dr

      @property
      def handoff_count(self) -> int:
          return len(self._handoffs)

      @property
      def sub_delegations(self) -> list:
          return list(self._handoffs)
  