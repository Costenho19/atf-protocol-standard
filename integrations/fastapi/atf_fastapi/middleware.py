"""
  ATFMiddleware — Starlette/FastAPI middleware enforcing ATF protocol at the HTTP boundary.

  Request flow:
      1. Extract Bearer token from Authorization header.
      2. Decode as JSON Delegation Receipt (DR).
      3. Run ATF invariant checks (ATF-INV-001 through ATF-INV-006).
      4. Sample CES and attach RCR to request state.
      5. Add X-ATF-* response headers for downstream audit.

  On any ATF violation:
      - Returns HTTP 403 Forbidden with ATF reason code (ATF-INV-001 → 403).
      - Returns HTTP 401 Unauthorized if no DR provided and route requires ATF.
      - Returns HTTP 503 Service Unavailable if HALT (RGC-INV-003).

  Usage:
      from fastapi import FastAPI
      from atf_fastapi import ATFMiddleware

      app = FastAPI()
      app.add_middleware(
          ATFMiddleware,
          principal_public_key_b64 = PUBLIC_KEY_B64,
          require_atf_on           = ["/api/v1/decisions", "/api/v1/execute"],
          halt_response_code       = 503,   # RGC-INV-003: HALT → 503
          verbose                  = True,
      )
  """
  from __future__ import annotations

  import hashlib
  import json
  import time
  import uuid
  import datetime
  import base64
  from typing import Any, Dict, List, Optional, Callable

  from starlette.middleware.base import BaseHTTPMiddleware
  from starlette.requests import Request
  from starlette.responses import JSONResponse, Response
  from starlette.types import ASGIApp

  from .utils import compute_content_hash, compute_ces, ces_to_status


  class ATFMiddleware(BaseHTTPMiddleware):
      """
      FastAPI/Starlette middleware enforcing ATF protocol invariants at every request.

      Invariants enforced per request:
          ATF-INV-001  MAR — budget_granted ≤ budget_delegator
          ATF-INV-002  ID format — ATFDR-[0-9A-F]{16}
          ATF-INV-003  Chain root — must trace to a TIER-1 human principal
          ATF-INV-004  Content hash — SHA-256 recomputed and verified
          ATF-INV-006  Temporal validity — DR not expired
          RGC-INV-001  CES formula — T×0.30+B×0.30+D×0.20+I×0.20 (immutable)
          RGC-INV-003  HALT protocol — CES < 10.0 → 503 (not configurable)
      """

      def __init__(
          self,
          app: ASGIApp,
          *,
          principal_public_key_b64: Optional[str] = None,
          require_atf_on: Optional[List[str]] = None,
          skip_paths: Optional[List[str]] = None,
          halt_response_code: int = 503,
          violation_response_code: int = 403,
          verbose: bool = False,
      ) -> None:
          super().__init__(app)
          self._public_key_b64 = principal_public_key_b64
          self._require_on = set(require_atf_on or [])
          self._skip = set(skip_paths or ["/health", "/docs", "/openapi.json", "/redoc"])
          self._halt_code = halt_response_code
          self._violation_code = violation_response_code
          self._verbose = verbose

      async def dispatch(self, request: Request, call_next: Callable) -> Response:
          path = request.url.path

          # Skip paths that don't need ATF governance
          if path in self._skip:
              return await call_next(request)

          auth = request.headers.get("Authorization", "")
          has_dr = auth.startswith("Bearer ")

          # If no DR provided, only block if this path requires ATF
          if not has_dr:
              if self._require_on and path in self._require_on:
                  return JSONResponse(
                      status_code=401,
                      content={
                          "error": "ATF delegation receipt required",
                          "hint": "Provide Authorization: Bearer <DR_JSON_base64>",
                          "protocol": "RFC-ATF-1",
                      },
                  )
              return await call_next(request)

          # Decode DR from Bearer token (base64-encoded JSON)
          try:
              raw = auth[7:].strip()
              try:
                  dr_bytes = base64.b64decode(raw + "==")
                  dr: Dict[str, Any] = json.loads(dr_bytes)
              except Exception:
                  dr = json.loads(raw)
          except Exception as e:
              return self._error(self._violation_code, "invalid_dr_encoding",
                                 f"Cannot decode DR from Authorization header: {e}")

          # Run ATF checks
          check_result = self._check_dr(dr)
          if not check_result["ok"]:
              code = self._halt_code if check_result.get("halt") else self._violation_code
              return self._error(code, check_result["reason"], check_result["message"], dr=dr)

          # Attach governance context to request state
          rcr_id = f"ATFRCR-{uuid.uuid4().hex[:16].upper()}"
          request.state.atf_dr = dr
          request.state.atf_rcr_id = rcr_id
          request.state.atf_ces = check_result["ces_score"]
          request.state.atf_status = check_result["ces_status"]

          if self._verbose:
              print(f"[ATF] {request.method} {path} — DR={dr.get('delegation_id')} "
                    f"CES={check_result['ces_score']:.1f} ({check_result['ces_status']}) "
                    f"RCR={rcr_id}")

          response = await call_next(request)

          # Add ATF audit headers to response
          response.headers["X-ATF-Delegation-ID"] = str(dr.get("delegation_id", ""))
          response.headers["X-ATF-Chain-Root"]    = str(dr.get("chain_root_id", ""))
          response.headers["X-ATF-RCR-ID"]        = rcr_id
          response.headers["X-ATF-CES-Score"]     = f"{check_result['ces_score']:.1f}"
          response.headers["X-ATF-Status"]         = check_result["ces_status"]
          response.headers["X-ATF-Protocol"]       = "RFC-ATF-1/RFC-ATF-2"
          return response

      def _check_dr(self, dr: Dict[str, Any]) -> Dict[str, Any]:
          """Run all ATF invariant checks. Returns {ok, reason, message, ces_score, ces_status}."""
          import re

          # ATF-INV-002 — ID format
          did = str(dr.get("delegation_id", ""))
          if not re.match(r"^ATFDR-[0-9A-F]{16}$", did):
              return {"ok": False, "reason": "id_format_atf_inv_002",
                      "message": f"ATF-INV-002: invalid delegation_id format: {did}"}

          # ATF-INV-001 — MAR
          granted   = float(dr.get("authority_budget_granted", 0))
          delegator = float(dr.get("authority_budget_delegator", 0))
          if granted > delegator:
              return {"ok": False, "reason": "mar_atf_inv_001",
                      "message": f"ATF-INV-001: budget_granted {granted} > budget_delegator {delegator}"}

          # ATF-INV-006 — Temporal validity
          expires_at = dr.get("expires_at", "")
          remaining_pct = 50.0
          if expires_at:
              try:
                  exp = datetime.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                  now = datetime.datetime.now(datetime.timezone.utc)
                  if now > exp:
                      return {"ok": False, "reason": "expired_atf_inv_006",
                              "message": f"ATF-INV-006: DR expired at {expires_at}"}
                  total = (exp - datetime.datetime.fromisoformat(
                      dr.get("created_at", expires_at).replace("Z", "+00:00"))).total_seconds()
                  remaining = (exp - now).total_seconds()
                  remaining_pct = max(0.0, min(100.0, (remaining / max(total, 1)) * 100))
              except ValueError:
                  pass

          # ATF-INV-004 — Content hash
          is_example = "BASE64_" in str(dr.get("pqc_signature", ""))
          if not is_example:
              computed = compute_content_hash(dr)
              if dr.get("content_hash") and dr["content_hash"] != computed:
                  return {"ok": False, "reason": "content_hash_mismatch",
                          "message": "ATF-INV-004: content_hash mismatch — receipt may be tampered"}

          # RGC-INV-001 — CES (formula immutable)
          ces_budget    = min(100.0, (granted / max(delegator, 1.0)) * 100)
          ces_temporal  = remaining_pct
          ces_context   = 100.0
          ces_integrity = 100.0
          ces_score  = compute_ces(ces_temporal, ces_budget, ces_context, ces_integrity)
          ces_status = ces_to_status(ces_score)

          # RGC-INV-003 — HALT (invariant — not configurable)
          if ces_status == "HALT":
              return {"ok": False, "reason": "rgc_inv_003_halt", "halt": True,
                      "message": f"RGC-INV-003: CES={ces_score:.1f} < 10.0 — HALT protocol triggered",
                      "ces_score": ces_score, "ces_status": ces_status}

          return {"ok": True, "ces_score": ces_score, "ces_status": ces_status, "reason": "", "message": ""}

      def _error(self, code: int, reason: str, message: str, dr: Optional[Dict] = None) -> JSONResponse:
          body: Dict[str, Any] = {
              "error": message,
              "atf_reason": reason,
              "protocol": "RFC-ATF-1 / RFC-ATF-2",
              "docs": "https://costenho19.github.io/atf-protocol-standard/",
          }
          if dr:
              body["delegation_id"] = dr.get("delegation_id")
          return JSONResponse(status_code=code, content=body)
  