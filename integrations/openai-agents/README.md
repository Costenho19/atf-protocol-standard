# atf-openai-agents

  **ATF Protocol governance for OpenAI Agents SDK** — delegation receipts, runtime continuity monitoring, and HALT protocol at every agent run and handoff.

  [![ATF-RGC Conformant](https://img.shields.io/badge/ATF--RGC--Conformant-v1.0.0-58a6ff?style=flat-square)](https://costenho19.github.io/atf-protocol-standard/conformance/)
  [![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](https://python.org)

  ## Installation

  ```bash
  pip install atf-openai-agents
  # With OpenAI Agents SDK:
  pip install "atf-openai-agents[agents]"
  ```

  ## Guard any OpenAI Agent run

  ```python
  from atf_openai_agents import ATFAgentGuard
  import agents  # openai-agents

  guard = ATFAgentGuard(dr=delegation_receipt, principal_id="HUMAN-harold-nunes-001")
  result = await guard.run_async(agent=my_agent, input="Analyze AAPL risk \$500k")

  print(guard.governance_report())
  # {
  #   "delegation_id": "ATFDR-3A7F9B2C1D4E5F6A",
  #   "runs": 1,
  #   "status_summary": {"NOMINAL": 1},
  # }
  ```

  ## Multi-agent handoff governance

  ```python
  from atf_openai_agents import ATFHandoffGuard

  handoff_guard = ATFHandoffGuard(parent_dr=parent_dr)

  # Sub-delegation: 60% of parent budget (ATF-INV-001 validated)
  sub_dr = handoff_guard.authorize_handoff(
      to_agent_id="AID-FINANCE-9B8C7D6E5F4A3B2C",
      task_scope={"action": "risk_analysis", "domain": "FINANCE"},
      budget_fraction=0.6,
  )
  ```

  ## RunHooks (Agents SDK native)

  ```python
  from agents import Runner
  from atf_openai_agents import ATFRunHooks

  hooks = ATFRunHooks(dr=dr, principal_id="HUMAN-harold-nunes-001")
  result = await Runner.run(agent, input="...", hooks=hooks)
  print(hooks.governance_summary())
  ```

  ## References

  - RFC-ATF-1: DOI [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
  - RFC-ATF-2: SSRN [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
  