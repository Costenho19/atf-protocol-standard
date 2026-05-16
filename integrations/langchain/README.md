# atf-langchain

  **ATF Protocol governance layer for LangChain** — enforces RFC-ATF-1/2/3 invariants at every LLM call, tool invocation, and chain execution.

  [![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-v1.0.0-3fb950?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjIiIGhlaWdodD0iMjIiIHZpZXdCb3g9IjAgMCAyMiAyMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cG9seWdvbiBwb2ludHM9IjExLDIgMjAsNyAyMCwxNSAxMSwyMCAyLDE1IDIsNyIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjM2ZiOTUwIiBzdHJva2Utd2lkdGg9IjEuNSIvPjwvc3ZnPg==)](https://costenho19.github.io/atf-protocol-standard/conformance/)
  [![Protocol](https://img.shields.io/badge/Protocol-RFC--ATF--1%2F2%2F3-58a6ff?style=flat-square)](https://costenho19.github.io/atf-protocol-standard/)
  [![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](https://python.org)
  [![License](https://img.shields.io/badge/license-CC--BY--4.0-gold?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

  ---

  ## What it does

  Every time your LangChain chain, agent, or tool executes, `atf-langchain` verifies that:

  | Check | Invariant | What it catches |
  |---|---|---|
  | Authority budget | ATF-INV-001 (MAR) | Agent acting beyond delegated authority |
  | Receipt integrity | ATF-INV-004 | Tampered or forged delegation receipts |
  | Temporal validity | ATF-INV-006 | Expired delegation windows |
  | Runtime health | RGC-INV-001 | CES score below threshold |
  | **HALT protocol** | **RGC-INV-003** | **CES < 10.0 → execution ceases immediately** |

  The HALT threshold (10.0) is a **protocol invariant** — not a configuration option.

  ---

  ## Installation

  ```bash
  pip install atf-langchain
  # With PQC signature verification:
  pip install "atf-langchain[pqc]"
  ```

  ---

  ## Quick start

  ```python
  from langchain_openai import ChatOpenAI
  from atf_langchain import ATFCallbackHandler

  # Your delegation receipt (from atf-core or OMNIX API)
  dr = {
      "delegation_id": "ATFDR-3A7F9B2C1D4E5F6A",
      "delegator_id": "HUMAN-harold-nunes-001",
      "delegate_id": "AID-FINANCE-9B8C7D6E5F4A3B2C",
      "task_scope": {"action": "equity_order_execution", "domain": "FINANCE"},
      "authority_budget_delegator": 100.0,
      "authority_budget_granted": 60.0,
      "chain_root_id": "ATFDR-3A7F9B2C1D4E5F6A",
      "content_hash": "sha256:...",
      "pqc_signature": "...",
      "pqc_algorithm": "dilithium3",
      "expires_at": "2026-06-01T00:00:00Z",
      "status": "ACTIVE",
  }

  handler = ATFCallbackHandler(
      dr=dr,
      principal_id="HUMAN-harold-nunes-001",
      on_halt="raise",   # ATF-INV-003: raise ATFHaltError if CES < 10.0
  )

  llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[handler])
  result = llm.invoke("Analyze risk for AAPL equity position \$500k USD")

  # Inspect governance activity
  print(handler.governance_report())
  # {
  #   "delegation_id": "ATFDR-3A7F9B2C1D4E5F6A",
  #   "invocations": 1,
  #   "rcr_count": 1,
  #   "status_summary": {"NOMINAL": 1},
  # }
  ```

  ---

  ## LCEL / Runnable interface

  ```python
  from atf_langchain import ATFGovernedRunnable
  from langchain_openai import ChatOpenAI
  from langchain_core.prompts import ChatPromptTemplate

  chain = ChatPromptTemplate.from_template("{input}") | ChatOpenAI()

  governed_chain = ATFGovernedRunnable(
      runnable=chain,
      dr=dr,
      principal_id="HUMAN-harold-nunes-001",
  )

  result = governed_chain.invoke({"input": "Summarize AAPL risk factors"})
  print(governed_chain.governance_report)
  ```

  ---

  ## LangChain Tools

  ```python
  from langchain.agents import initialize_agent
  from atf_langchain import ATFVerifierTool, ATFIssueTool

  tools = [
      ATFVerifierTool(issuer_public_key_b64=PUBLIC_KEY),
      ATFIssueTool(principal_id="HUMAN-harold-nunes-001", principal_budget=100.0),
  ]

  agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
  # Agent can now verify and issue DRs as part of its reasoning loop.
  ```

  ---

  ## ATF-RGC-Compliant

  This integration claims **ATF-RGC-Compliant** (Tier 2) because it enforces:
  - All 6 ATF-Compliant invariants (ATF-INV-001–006)
  - RGC-INV-001 (CES formula — immutable)
  - RGC-INV-002 (RCR chain integrity — predecessor linkage)
  - RGC-INV-003 (HALT protocol — CES < 10.0)
  - RGC-INV-004 (Escalation event on HALT)

  See [Conformance Program](https://costenho19.github.io/atf-protocol-standard/conformance/) to claim your badge.

  ---

  ## References

  - RFC-ATF-1: DOI [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016) · SSRN [6757339](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339)
  - RFC-ATF-2: SSRN [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
  - [Interactive Diagrams](https://costenho19.github.io/atf-protocol-standard/diagrams/)
  - [Technical Whitepaper](https://costenho19.github.io/atf-protocol-standard/whitepaper/)
  