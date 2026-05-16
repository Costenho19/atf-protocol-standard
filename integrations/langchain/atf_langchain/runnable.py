"""
  ATFGovernedRunnable — wraps any LangChain Runnable with ATF governance.

  Provides a clean LCEL-compatible interface:
      chain = ATFGovernedRunnable(runnable=your_chain, dr=dr, tar=tar, ...)
      result = chain.invoke({"input": "..."})

  Every invoke() call triggers a full ATF governance check before execution.
  """
  from __future__ import annotations
  from typing import Any, Dict, Optional
  from langchain_core.runnables import Runnable, RunnableConfig
  from .handler import ATFCallbackHandler

  class ATFGovernedRunnable(Runnable):
      """Wraps any LangChain Runnable with ATF protocol governance."""

      def __init__(
          self,
          *,
          runnable: Runnable,
          dr: Dict[str, Any],
          tar: Optional[Dict[str, Any]] = None,
          principal_id: str,
          on_halt: str = "raise",
          verbose: bool = False,
      ) -> None:
          self._inner = runnable
          self._handler = ATFCallbackHandler(
              dr=dr, tar=tar, principal_id=principal_id,
              on_halt=on_halt, verbose=verbose,
          )

      def invoke(self, input: Any, config: Optional[RunnableConfig] = None) -> Any:
          cfg = config or {}
          callbacks = list(cfg.get("callbacks", []) or [])
          callbacks.append(self._handler)
          cfg["callbacks"] = callbacks
          return self._inner.invoke(input, cfg)

      async def ainvoke(self, input: Any, config: Optional[RunnableConfig] = None) -> Any:
          cfg = config or {}
          callbacks = list(cfg.get("callbacks", []) or [])
          callbacks.append(self._handler)
          cfg["callbacks"] = callbacks
          return await self._inner.ainvoke(input, cfg)

      @property
      def governance_report(self) -> Dict[str, Any]:
          return self._handler.governance_report()
  