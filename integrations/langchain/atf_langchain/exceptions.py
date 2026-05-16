"""
  ATF-specific exceptions for the LangChain integration.
  All exceptions carry the ATF reason code for programmatic handling.
  """

  from __future__ import annotations
  from typing import Optional


  class ATFError(Exception):
      """Base class for all ATF protocol errors."""
      def __init__(self, message: str, *, reason: str = "", delegation_id: Optional[str] = None):
          super().__init__(message)
          self.reason = reason
          self.delegation_id = delegation_id


  class ATFHaltError(ATFError):
      """
      Raised when CES < 10.0 (RGC-INV-003 — HALT Protocol).

      This is a protocol invariant, not a configuration option.
      The LangChain chain/agent MUST stop execution and require
      reauthorization from the delegating principal.

      Attributes:
          ces_score: The CES score that triggered HALT.
          delegation_id: The DR that was in effect at HALT time.
      """
      def __init__(self, message: str, *, ces_score: float, delegation_id: Optional[str] = None):
          super().__init__(message, reason="rgc_inv_003_halt", delegation_id=delegation_id)
          self.ces_score = ces_score


  class ATFViolationError(ATFError):
      """
      Raised when an ATF protocol invariant is violated (ATF-INV-001 through ATF-INV-006).

      Attributes:
          reason: Normative reason code (FVP-INV-007 — stable across all ATF ports).
      """
      pass


  class ATFExpiredError(ATFError):
      """Raised when a DR or TAR has expired (ATF-INV-006)."""
      def __init__(self, message: str, *, expired_at: str, delegation_id: Optional[str] = None):
          super().__init__(message, reason="expired_atf_inv_006", delegation_id=delegation_id)
          self.expired_at = expired_at
  