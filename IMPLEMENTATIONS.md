# Known Implementations — ATF Protocol Standard

  This file catalogs known implementations of the Agent Trust Fabric protocol.
  To add your implementation, open a Pull Request updating this file.

  ---

  ## Reference Implementation

  ### atf-core (Python)

  | Property | Value |
  |---|---|
  | **Repository** | [atf-protocol-standard/reference-implementation](./reference-implementation/) |
  | **Language** | Python 3.9+ |
  | **Status** | Active |
  | **Maintainer** | OMNIX QUANTUM LTD |
  | **Install** | `pip install -e reference-implementation/` |

  **Compliance:**

  | Profile | Status | Invariants Covered |
  |---|---|---|
  | ATF-Compliant (L1–L3) | ✅ Conformant | ATF-INV-001, 002, 003, 004, 005 |
  | ATF-RGC-Compliant (L1–L4) | ✅ Conformant | + RGC-INV-001, 002, 003 |
  | ATF-FEI-Compliant (L1–L5) | 🔶 Partial | L5 pipeline in progress |

  **Cryptographic library:** pypqc (ML-DSA-65 / Dilithium-3)
  **Platforms:** Linux, macOS, Windows (Python 3.9+)

  ---

  ## Production Implementation

  ### OMNIX QUANTUM Decision Governance Platform

  | Property | Value |
  |---|---|
  | **Organization** | OMNIX QUANTUM LTD |
  | **Website** | https://omnixquantum.com |
  | **Stack** | Python 3.11 · Flask · PostgreSQL · Redis |
  | **Status** | Production — deployed on Railway |

  **Compliance:**

  | Profile | Status |
  |---|---|
  | ATF-FEI-Compliant (L1–L5) | ✅ Full — all 40 invariants enforced |

  **Extensions beyond the open standard:**
  - Telegram bot governance interface
  - AI fallback chain: GPT-4o-mini → GPT-4o → Gemini 2.5 Flash → Claude
  - Web dashboard with real-time receipt verification
  - B2B API with API key provisioning
  - Adaptive Veto Machine (AVM) — threshold-based approval gate

  ---

  
  ## TypeScript Port

  ### @atf-protocol/verifier (TypeScript / Node.js)

  | Property | Value |
  |---|---|
  | **Path** | [`ports/typescript/`](./ports/typescript/) |
  | **Language** | TypeScript / Node.js 18+ |
  | **Status** | Beta |
  | **Maintainer** | OMNIX QUANTUM LTD |
  | **Install** | `cd ports/typescript && npm install` *(npm: Q3 2026)* |

  **Compliance:**

  | Profile | Status | Invariants Covered |
  |---|---|---|
  | ATF-RGC-Compliant (L1–L4) | 🔶 Beta | ATF-INV-001–006, RGC-INV-001–004 (11 invariants) |

  **Cross-language parity:** FVP-INV-007 determinism verified — identical output to Python reference for all 34 conformance vectors.
  **Cryptographic library:** Inline pure-TS SHA-256 (no external deps for hashing)

  ---

  ## Community Implementations

  *No community implementations registered yet.*

  To register your implementation:
  1. Fork this repository
  2. Add an entry to this file following the template below
  3. Open a Pull Request

  ### Template

  ```markdown
  ### [Implementation Name] (Language)

  | Property | Value |
  |---|---|
  | **Repository** | Link |
  | **Language** | Language + version |
  | **Status** | Active / Experimental / Archived |
  | **Maintainer** | Name or organization |

  **Compliance:**

  | Profile | Status | Invariants Covered |
  |---|---|---|
  | ATF-Compliant | ✅ / 🔶 / ❌ | ATF-INV-XXX |

  **Cryptographic library:** Library name
  **Platforms:** OS and runtime requirements
  **Notes:** Any deviations or extensions

  **Conformance evidence:** Link to CI or test output
  ```

  ---

  ## Porting to Other Languages

  We actively encourage implementations in:

  | Language | Status | Notes |
  |---|---|---|
  | **Go** | ❌ Not yet | High priority — ideal for server-side integration |
  | **TypeScript / Node.js** | 🔶 [`ports/typescript/`](./ports/typescript/) — beta | ATF-RGC-Compliant (11 invariants) |
  | **Rust** | 🔶 [`ports/rust/`](./ports/rust/) — skeleton ready | Implement 3 functions → all 34 vectors pass |
  | **Java / Kotlin** | ❌ Not yet | Enterprise integration |

  Port requirements: See [CONTRIBUTING.md](./CONTRIBUTING.md#language-ports)

  ---

  ## Rust Port Skeleton

| Property | Value |
|---|---|
| **Path** | [`ports/rust/`](./ports/rust/) |
| **Language** | Rust (edition 2021) |
| **Status** | Skeleton — implementation contributions welcome |
| **Maintainer** | OMNIX QUANTUM LTD (skeleton) |

**Compliance target:** `ATF-RGC-Compliant` (14 invariants across ATF-INV-001–006 + RGC-INV-001–004)

What is complete: all type definitions, reason codes, CES helpers, CLI binary,
and conformance harness loading all 34 official vectors.

What needs implementation: `compute_content_hash()`, `verify_delegation_receipt()`,
`verify_runtime_continuity_record()` — three functions total.

Getting started: `cargo test` — make all 34 vectors pass.
See [`ports/rust/README.md`](./ports/rust/README.md) and
[`ports/rust/PORTING_GUIDE.md`](./ports/rust/PORTING_GUIDE.md).

---
*OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
  