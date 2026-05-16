# ATF Protocol — Integration Ecosystem

  ATF Protocol integrations for popular AI frameworks.

  | Integration | Framework | Badge | Install |
  |---|---|---|---|
  | **atf-langchain** | LangChain / LCEL | ATF-RGC-Compliant | `pip install -e ./integrations/langchain` *(PyPI: Q3 2026)* |
  | **atf-fastapi** | FastAPI / Starlette | ATF-Compliant | `pip install -e ./integrations/fastapi` *(PyPI: Q3 2026)* |
  | **atf-openai-agents** | OpenAI Agents SDK | ATF-Compliant | `pip install -e ./integrations/openai-agents` *(PyPI: Q3 2026)* |

  All integrations enforce:
  - **ATF-INV-001** — Monotonic Authority Reduction (MAR): budget_granted ≤ budget_delegator
  - **ATF-INV-004** — Content hash integrity (SHA-256, FVP-INV-007)
  - **ATF-INV-006** — Temporal validity: DR not expired
  - **RGC-INV-001** — CES formula immutability: T×0.30 + B×0.30 + D×0.20 + I×0.20
  - **RGC-INV-003** — HALT protocol: CES < 10.0 → execution ceases (not configurable)

  Each integration directory includes:
  - Full Python package (`pyproject.toml`, `README.md`)
  - Type-annotated source with comprehensive docstrings
  - Production-ready error handling with ATF reason codes (FVP-INV-007)

  See [conformance program](https://costenho19.github.io/atf-protocol-standard/conformance/)
  to claim your ATF-Compliant badge for your own integration.

  ## References

  - Protocol: [costenho19.github.io/atf-protocol-standard](https://costenho19.github.io/atf-protocol-standard/)
  - RFC-ATF-1: DOI [10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016)
  - RFC-ATF-2: SSRN [6763978](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6763978)
  