"""
  atf-langchain — Agent Trust Fabric governance layer for LangChain.

  Enforces ATF protocol invariants (RFC-ATF-1/2/3) on LangChain chains,
  agents, and runnables at runtime — before every LLM call and tool invocation.

  Installation:
      pip install atf-langchain langchain

  Quick start:
      from atf_langchain import ATFCallbackHandler, atf_governed
      from langchain_openai import ChatOpenAI

      dr  = issue_delegation_receipt(...)   # from atf-core
      tar = issue_temporal_record(...)

      llm = ChatOpenAI()
      guarded = llm.with_config(callbacks=[ATFCallbackHandler(dr=dr, tar=tar)])
      result  = guarded.invoke("Analyze risk for AAPL position \$500k")
  """

  from .handler  import ATFCallbackHandler
  from .tool     import ATFVerifierTool, ATFIssueTool
  from .runnable import ATFGovernedRunnable
  from .deps     import atf_required, ATFContext

  __version__ = "1.0.0"
  __protocol__ = "RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3"

  __all__ = [
      "ATFCallbackHandler",
      "ATFVerifierTool",
      "ATFIssueTool",
      "ATFGovernedRunnable",
      "atf_required",
      "ATFContext",
  ]
  