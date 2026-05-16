"""
  atf-openai-agents — ATF Protocol governance for OpenAI Agents SDK.

  Wraps OpenAI Agents (Swarm, Assistants API, and the new Agents SDK) with
  full ATF governance — delegation receipts, runtime continuity monitoring,
  and HALT enforcement — at every agent handoff and tool call.

  Installation:
      pip install atf-openai-agents openai

  Quick start:
      from atf_openai_agents import ATFAgentGuard, ATFHandoffGuard
      from openai import OpenAI

      guard = ATFAgentGuard(dr=dr, principal_id="HUMAN-harold-nunes-001")
      result = guard.run(agent=my_agent, messages=[...])
  """

  from .guard    import ATFAgentGuard
  from .handoff  import ATFHandoffGuard
  from .hooks    import ATFRunHooks
  from .exceptions import ATFHaltError, ATFViolationError

  __version__ = "1.0.0"
  __protocol__ = "RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3"

  __all__ = [
      "ATFAgentGuard",
      "ATFHandoffGuard",
      "ATFRunHooks",
      "ATFHaltError",
      "ATFViolationError",
  ]
  