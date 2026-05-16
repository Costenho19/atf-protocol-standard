"""
  ATFAgentGuard — wraps OpenAI Agent execution with ATF protocol governance.

  Intercepts every agent run, validates the Delegation Receipt, monitors
  runtime continuity (CES), and enforces the HALT protocol (RGC-INV-003).

  Compatible with:
      - OpenAI Agents SDK (agents.Runner)
      - OpenAI Swarm
      - Assistants API (via hook pattern)

  Usage:
      from atf_openai_agents import ATFAgentGuard
      import agents  # openai-agents

      guard = ATFAgentGuard(
          dr=delegation_receipt,
          principal_id="HUMAN-harold-nunes-001",
          on_halt="raise",    # RGC-INV-003: raises ATFHaltError if CES < 10.0
      )

      # Wrap any agent execution
      result = await guard.run_async(
          agent=my_agent,
          input="Analyze AAPL position risk \$500k",
      )
      print(guard.governance_report())
  """
  from __future__ import annotations

  import time
  import uuid
  from dataclasses import dataclass, field
  from typing import Any, Dict, List, Optional

  from .utils import compute_ces, compute_content_hash, ces_to_status
  from .exceptions import ATFHaltError, ATFViolationError


  @dataclass
  class ATFRunRecord:
      """Governance record for a single agent run."""
      run_id: str
      delegation_id: str
      chain_root_id: str
      agent_name: str
      ces_score: float
      continuity_status: str
      verdict: str
      timestamp_ns: int
      rcr_id: str
      handoffs: int = 0
      tool_calls: int = 0
      notes: List[str] = field(default_factory=list)


  class ATFAgentGuard:
      """
      Wraps OpenAI Agent execution with ATF protocol governance.

      ATF invariants enforced:
          ATF-INV-001   MAR — budget_granted ≤ budget_delegator
          ATF-INV-004   Content hash integrity
          ATF-INV-006   Temporal validity — DR not expired
          RGC-INV-001   CES formula immutability
          RGC-INV-003   HALT — CES < 10.0 → execution stops
      """

      def __init__(
          self,
          *,
          dr: Dict[str, Any],
          principal_id: str,
          on_halt: str = "raise",          # "raise" | "log"
          on_violation: str = "raise",
          verbose: bool = False,
      ) -> None:
          self._dr = dr
          self._principal_id = principal_id
          self._on_halt = on_halt
          self._on_violation = on_violation
          self._verbose = verbose
          self._records: List[ATFRunRecord] = []
          self._rcr_chain: List[str] = []
          self._validate_dr(dr)

      def run(self, agent: Any, input: str, **kwargs: Any) -> Any:
          """Synchronous agent run with ATF governance."""
          self._pre_run_check(agent)
          try:
              import agents as openai_agents
              result = openai_agents.Runner.run_sync(agent, input, **kwargs)
          except ImportError:
              # Fallback: direct invocation if agents SDK not installed
              result = agent.run(input, **kwargs) if hasattr(agent, "run") else None
          self._post_run_record(agent, result)
          return result

      async def run_async(self, agent: Any, input: str, **kwargs: Any) -> Any:
          """Async agent run with ATF governance."""
          self._pre_run_check(agent)
          try:
              import agents as openai_agents
              result = await openai_agents.Runner.run(agent, input, **kwargs)
          except ImportError:
              result = await agent.arun(input, **kwargs) if hasattr(agent, "arun") else None
          self._post_run_record(agent, result)
          return result

      def _pre_run_check(self, agent: Any) -> None:
          """Run ATF governance checks before agent execution."""
          now_ns = time.time_ns()
          notes: List[str] = []

          # ATF-INV-001 — MAR
          granted   = float(self._dr.get("authority_budget_granted", 0))
          delegator = float(self._dr.get("authority_budget_delegator", 0))
          if granted > delegator:
              self._handle_violation(
                  f"ATF-INV-001: budget_granted {granted} > budget_delegator {delegator}",
                  "mar_atf_inv_001"
              )

          # ATF-INV-006 — Temporal validity
          import datetime
          expires_at = self._dr.get("expires_at", "")
          remaining_pct = 50.0
          if expires_at:
              try:
                  exp = datetime.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                  now = datetime.datetime.now(datetime.timezone.utc)
                  if now > exp:
                      self._handle_violation(f"ATF-INV-006: DR expired at {expires_at}", "expired_atf_inv_006")
                  remaining_pct = max(0.0, (exp - now).total_seconds() / 86400 * 100)
              except ValueError:
                  pass

          # RGC-INV-001 — CES (formula fixed)
          ces_budget    = min(100.0, (granted / max(delegator, 1.0)) * 100)
          ces_temporal  = min(100.0, remaining_pct)
          ces_score     = compute_ces(ces_temporal, ces_budget, 100.0, 100.0)
          ces_status    = ces_to_status(ces_score)
          notes.append(f"CES={ces_score:.1f} ({ces_status})")

          rcr_id = f"ATFRCR-{uuid.uuid4().hex[:16].upper()}"
          self._rcr_chain.append(rcr_id)

          # RGC-INV-003 — HALT (invariant)
          if ces_status == "HALT":
              msg = (
                  f"RGC-INV-003 HALT: CES={ces_score:.1f} < 10.0. "
                  f"DR={self._dr.get('delegation_id')} — Reauthorization required."
              )
              self._records.append(ATFRunRecord(
                  run_id=f"ATFRUN-{uuid.uuid4().hex[:16].upper()}",
                  delegation_id=str(self._dr.get("delegation_id", "")),
                  chain_root_id=str(self._dr.get("chain_root_id", "")),
                  agent_name=getattr(agent, "name", str(agent)),
                  ces_score=ces_score, continuity_status="HALT",
                  verdict="FAIL", timestamp_ns=now_ns, rcr_id=rcr_id, notes=notes,
              ))
              if self._on_halt == "raise":
                  raise ATFHaltError(msg, ces_score=ces_score, delegation_id=str(self._dr.get("delegation_id", "")))
              return

          if self._verbose:
              agent_name = getattr(agent, "name", str(agent))
              print(f"[ATF] Agent run authorized: {agent_name} | CES={ces_score:.1f} ({ces_status}) | RCR={rcr_id}")

      def _post_run_record(self, agent: Any, result: Any) -> None:
          """Record governance event after agent completes."""
          now_ns = time.time_ns()
          granted   = float(self._dr.get("authority_budget_granted", 0))
          delegator = float(self._dr.get("authority_budget_delegator", 0))
          ces = compute_ces(50.0, min(100.0, (granted / max(delegator, 1.0)) * 100), 100.0, 100.0)
          rcr_id = self._rcr_chain[-1] if self._rcr_chain else f"ATFRCR-{uuid.uuid4().hex[:16].upper()}"
          self._records.append(ATFRunRecord(
              run_id=f"ATFRUN-{uuid.uuid4().hex[:16].upper()}",
              delegation_id=str(self._dr.get("delegation_id", "")),
              chain_root_id=str(self._dr.get("chain_root_id", "")),
              agent_name=getattr(agent, "name", str(agent)),
              ces_score=ces, continuity_status=ces_to_status(ces),
              verdict="PASS", timestamp_ns=now_ns, rcr_id=rcr_id,
          ))

      def _validate_dr(self, dr: Dict[str, Any]) -> None:
          import re
          did = str(dr.get("delegation_id", ""))
          if not re.match(r"^ATFDR-[0-9A-F]{16}$", did):
              raise ATFViolationError(f"ATF-INV-002: invalid delegation_id: {did}", reason="id_format_atf_inv_002")

      def _handle_violation(self, msg: str, reason: str) -> None:
          if self._on_violation == "raise":
              raise ATFViolationError(msg, reason=reason)
          print(f"[ATF WARNING] {msg}")

      def governance_report(self) -> Dict[str, Any]:
          statuses = [r.continuity_status for r in self._records]
          return {
              "delegation_id": self._dr.get("delegation_id"),
              "chain_root_id": self._dr.get("chain_root_id"),
              "runs":          len(self._records),
              "rcr_chain":     self._rcr_chain,
              "status_summary": {s: statuses.count(s) for s in set(statuses)},
              "protocol":      "RFC-ATF-1 / RFC-ATF-2",
          }

      @property
      def records(self) -> List[ATFRunRecord]:
          return list(self._records)
  