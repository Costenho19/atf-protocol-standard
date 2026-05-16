"""
  ATFDepends + require_atf — FastAPI dependency injection for per-route ATF governance.

  Usage:
      from fastapi import FastAPI, Depends
      from atf_fastapi import require_atf, ATFRequest

      app = FastAPI()

      @app.post("/api/v1/decisions")
      async def create_decision(atf: ATFRequest = Depends(require_atf())):
          # atf.dr         — the verified Delegation Receipt dict
          # atf.rcr_id     — the committed RCR ID for this request
          # atf.ces_score  — CES score at admission
          # atf.chain_root — chain_root_id from the DR
          return {"status": "approved", "atf_rcr": atf.rcr_id}

      # Require minimum CES score:
      @app.post("/api/v1/execute")
      async def execute(atf: ATFRequest = Depends(require_atf(min_ces=50.0))):
          ...
  """
  from __future__ import annotations

  import json
  import base64
  from dataclasses import dataclass
  from typing import Any, Dict, Optional

  from fastapi import Request, HTTPException, Header
  from .utils import compute_ces, ces_to_status, compute_content_hash


  @dataclass
  class ATFRequest:
      """Verified ATF context attached to a FastAPI request."""
      dr: Dict[str, Any]
      rcr_id: str
      ces_score: float
      ces_status: str
      chain_root: str
      delegation_id: str
      budget_granted: float
      budget_delegator: float


  def require_atf(min_ces: float = 0.0, required_domain: Optional[str] = None):
      """
      FastAPI dependency that enforces ATF governance on a per-route basis.

      Args:
          min_ces: Minimum acceptable CES score (default: 0.0 — any non-HALT score).
          required_domain: If set, DR must match this governance domain.

      Returns:
          ATFRequest with verified DR, RCR ID, and CES score.
      """
      async def _dependency(request: Request, authorization: str = Header(default="")) -> ATFRequest:
          # Check if middleware already processed the DR
          if hasattr(request.state, "atf_dr"):
              return ATFRequest(
                  dr=request.state.atf_dr,
                  rcr_id=getattr(request.state, "atf_rcr_id", ""),
                  ces_score=getattr(request.state, "atf_ces", 0.0),
                  ces_status=getattr(request.state, "atf_status", "UNKNOWN"),
                  chain_root=request.state.atf_dr.get("chain_root_id", ""),
                  delegation_id=request.state.atf_dr.get("delegation_id", ""),
                  budget_granted=float(request.state.atf_dr.get("authority_budget_granted", 0)),
                  budget_delegator=float(request.state.atf_dr.get("authority_budget_delegator", 0)),
              )

          # Parse DR from header
          if not authorization.startswith("Bearer "):
              raise HTTPException(status_code=401, detail={
                  "error": "ATF delegation receipt required",
                  "hint": "Provide Authorization: Bearer <DR_JSON>",
                  "protocol": "RFC-ATF-1",
              })
          try:
              raw = authorization[7:].strip()
              try:
                  dr = json.loads(base64.b64decode(raw + "=="))
              except Exception:
                  dr = json.loads(raw)
          except Exception as e:
              raise HTTPException(status_code=403, detail={"error": f"Invalid DR: {e}"})

          # ATF-INV-001 — MAR
          granted   = float(dr.get("authority_budget_granted", 0))
          delegator = float(dr.get("authority_budget_delegator", 0))
          if granted > delegator:
              raise HTTPException(status_code=403, detail={
                  "error": f"ATF-INV-001: budget_granted {granted} > budget_delegator {delegator}",
                  "atf_reason": "mar_atf_inv_001",
              })

          # Domain check
          if required_domain:
              scope = dr.get("task_scope", {})
              dr_domain = scope.get("domain", "") if isinstance(scope, dict) else ""
              if dr_domain != required_domain:
                  raise HTTPException(status_code=403, detail={
                      "error": f"DR domain {dr_domain!r} does not match required {required_domain!r}",
                      "atf_reason": "domain_mismatch",
                  })

          # CES
          ces = compute_ces(100.0, min(100.0, (granted / max(delegator, 1.0)) * 100), 100.0, 100.0)
          status = ces_to_status(ces)

          if status == "HALT":
              raise HTTPException(status_code=503, detail={
                  "error": f"RGC-INV-003: CES={ces:.1f} < 10.0 — HALT protocol. Reauthorization required.",
                  "atf_reason": "rgc_inv_003_halt",
              })

          if min_ces > 0 and ces < min_ces:
              raise HTTPException(status_code=403, detail={
                  "error": f"CES={ces:.1f} below required minimum {min_ces}",
                  "atf_reason": "ces_below_minimum",
              })

          import uuid
          return ATFRequest(
              dr=dr, rcr_id=f"ATFRCR-{uuid.uuid4().hex[:16].upper()}",
              ces_score=ces, ces_status=status,
              chain_root=str(dr.get("chain_root_id", "")),
              delegation_id=str(dr.get("delegation_id", "")),
              budget_granted=granted, budget_delegator=delegator,
          )
      return _dependency


  # Convenience alias
  ATFDepends = require_atf
  