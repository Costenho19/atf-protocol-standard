# atf-fastapi

  **ATF Protocol governance middleware for FastAPI** — enforces RFC-ATF-1/2/3 at the HTTP boundary.

  [![ATF-Compliant](https://img.shields.io/badge/ATF--Compliant-v1.0.0-58a6ff?style=flat-square)](https://costenho19.github.io/atf-protocol-standard/conformance/)
  [![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](https://python.org)
  [![License](https://img.shields.io/badge/license-CC--BY--4.0-gold?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

  Every request to your governed endpoints must carry an ATF Delegation Receipt.
  The middleware verifies MAR (ATF-INV-001), hash integrity (ATF-INV-004), temporal validity (ATF-INV-006),
  CES health (RGC-INV-001), and enforces the HALT protocol (RGC-INV-003 — CES < 10.0 → 503).

  ## Installation

  ```bash
  pip install atf-fastapi
  ```

  ## Middleware (global enforcement)

  ```python
  from fastapi import FastAPI
  from atf_fastapi import ATFMiddleware

  app = FastAPI()
  app.add_middleware(
      ATFMiddleware,
      principal_public_key_b64 = PUBLIC_KEY_B64,
      require_atf_on           = ["/api/v1/decisions", "/api/v1/execute"],
      halt_response_code       = 503,   # RGC-INV-003
  )

  @app.post("/api/v1/decisions")
  async def create_decision(body: dict):
      # request.state.atf_dr, .atf_rcr_id, .atf_ces are available
      return {"status": "approved"}
  ```

  Every approved response includes:
  ```
  X-ATF-Delegation-ID: ATFDR-3A7F9B2C1D4E5F6A
  X-ATF-Chain-Root:    HUMAN-harold-nunes-001
  X-ATF-RCR-ID:       ATFRCR-A1B2C3D4E5F67890
  X-ATF-CES-Score:    94.4
  X-ATF-Status:       NOMINAL
  X-ATF-Protocol:     RFC-ATF-1/RFC-ATF-2
  ```

  ## Per-route dependency

  ```python
  from fastapi import FastAPI, Depends
  from atf_fastapi import require_atf, ATFRequest

  app = FastAPI()

  @app.post("/api/v1/trade")
  async def execute_trade(atf: ATFRequest = Depends(require_atf(min_ces=50.0, required_domain="FINANCE"))):
      return {
          "status":     "executed",
          "rcr_id":     atf.rcr_id,
          "ces_score":  atf.ces_score,
          "chain_root": atf.chain_root,
      }
  ```

  ## ATF response codes

  | Code | Reason | Invariant |
  |------|--------|-----------|
  | 401 | No DR provided | Required route |
  | 403 | MAR violation | ATF-INV-001 |
  | 403 | ID format | ATF-INV-002 |
  | 403 | Content hash | ATF-INV-004 |
  | 403 | DR expired | ATF-INV-006 |
  | **503** | **HALT protocol** | **RGC-INV-003** |

  ## References

  - RFC-ATF-1: DOI [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
  - RFC-ATF-2: SSRN [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
  - [Technical Whitepaper](https://costenho19.github.io/atf-protocol-standard/whitepaper/)
  