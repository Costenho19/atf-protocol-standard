"""
  ATFRunHooks — OpenAI Agents SDK RunHooks implementation for ATF governance.
  Compatible with the official openai-agents RunHooks interface.
  """
  from __future__ import annotations
  from typing import Any, Dict, Optional
  from .utils import compute_ces, ces_to_status
  from .exceptions import ATFHaltError
  import time, uuid

  class ATFRunHooks:
      """
      Implements the OpenAI Agents SDK RunHooks interface with ATF governance.

      Usage:
          from agents import Runner
          from atf_openai_agents import ATFRunHooks

          hooks = ATFRunHooks(dr=dr, principal_id="HUMAN-harold-nunes-001")
          result = await Runner.run(agent, input="...", hooks=hooks)
          print(hooks.governance_summary())
      """

      def __init__(self, *, dr: Dict[str, Any], principal_id: str, on_halt: str = "raise") -> None:
          self._dr = dr
          self._principal_id = principal_id
          self._on_halt = on_halt
          self._events: list = []
          self._rcr_chain: list = []

      async def on_agent_start(self, context: Any, agent: Any) -> None:
          now_ns = time.time_ns()
          granted   = float(self._dr.get("authority_budget_granted", 0))
          delegator = float(self._dr.get("authority_budget_delegator", 0))
          ces = compute_ces(80.0, min(100.0,(granted/max(delegator,1))*100), 100.0, 100.0)
          status = ces_to_status(ces)
          rcr_id = f"ATFRCR-{uuid.uuid4().hex[:16].upper()}"
          self._rcr_chain.append(rcr_id)
          self._events.append({"event":"agent_start","ces":ces,"status":status,"rcr":rcr_id,"ts_ns":now_ns})
          if status == "HALT":
              msg = f"RGC-INV-003: CES={ces:.1f} < 10.0 at agent_start. Reauth required."
              if self._on_halt == "raise":
                  raise ATFHaltError(msg, ces_score=ces, delegation_id=str(self._dr.get("delegation_id","")))

      async def on_tool_start(self, context: Any, agent: Any, tool: Any) -> None:
          self._events.append({"event":"tool_start","tool":getattr(tool,"name",str(tool)),"ts_ns":time.time_ns()})

      async def on_handoff(self, context: Any, from_agent: Any, to_agent: Any) -> None:
          self._events.append({"event":"handoff","from":getattr(from_agent,"name","?"),"to":getattr(to_agent,"name","?"),"ts_ns":time.time_ns()})

      async def on_agent_end(self, context: Any, agent: Any, output: Any) -> None:
          self._events.append({"event":"agent_end","ts_ns":time.time_ns()})

      def governance_summary(self) -> Dict[str, Any]:
          return {
              "delegation_id": self._dr.get("delegation_id"),
              "rcr_chain": self._rcr_chain,
              "events": len(self._events),
              "protocol": "RFC-ATF-1 / RFC-ATF-2",
          }
  