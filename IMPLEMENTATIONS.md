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
  | **TypeScript / Node.js** | ❌ Not yet | High priority — browser + edge deployments |
  | **Rust** | ❌ Not yet | Recommended for embedded / WASM |
  | **Java / Kotlin** | ❌ Not yet | Enterprise integration |

  Port requirements: See [CONTRIBUTING.md](./CONTRIBUTING.md#language-ports)

  ---

  *OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
  