"""ATFContext and atf_required — dependency injection helpers."""
  from __future__ import annotations
  from dataclasses import dataclass
  from typing import Any, Dict, Optional
  from .handler import ATFCallbackHandler

  @dataclass
  class ATFContext:
      """Runtime ATF context for the current LangChain session."""
      dr: Dict[str, Any]
      tar: Optional[Dict[str, Any]]
      principal_id: str
      handler: ATFCallbackHandler

  def atf_required(dr: Dict[str, Any], tar: Optional[Dict[str, Any]] = None, principal_id: str = "") -> ATFContext:
      """Create an ATFContext — call before starting a governed LangChain chain."""
      handler = ATFCallbackHandler(dr=dr, tar=tar, principal_id=principal_id)
      return ATFContext(dr=dr, tar=tar, principal_id=principal_id, handler=handler)
  