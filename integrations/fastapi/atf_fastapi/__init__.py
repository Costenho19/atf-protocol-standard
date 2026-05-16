"""
  atf-fastapi — ATF Protocol governance middleware for FastAPI.

  Enforces RFC-ATF-1/2/3 invariants at the HTTP layer before your
  endpoints execute. Every request carries an ATF Delegation Receipt
  in the Authorization header; every response includes the RCR ID.

  Installation:
      pip install atf-fastapi fastapi

  Quick start:
      from fastapi import FastAPI
      from atf_fastapi import ATFMiddleware

      app = FastAPI()
      app.add_middleware(ATFMiddleware, principal_public_key_b64=PUBLIC_KEY)
  """

  from .middleware  import ATFMiddleware
  from .depends    import ATFDepends, ATFRequest, require_atf
  from .exceptions import ATFHTTPException, ATFHaltHTTPException

  __version__ = "1.0.0"
  __protocol__ = "RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3"

  __all__ = [
      "ATFMiddleware",
      "ATFDepends",
      "ATFRequest",
      "require_atf",
      "ATFHTTPException",
      "ATFHaltHTTPException",
  ]
  