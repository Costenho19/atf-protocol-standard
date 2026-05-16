# ATF Conformance Suite

**Standalone, platform-independent conformance verification for the Agent Trust Fabric protocol stack.**

The ATF Conformance Suite is the normative mechanism by which any implementation of RFC-ATF-1, RFC-ATF-2, or RFC-ATF-3 may verify and declare conformance. It runs without the OMNIX platform, without network access, and without any dependency on the reference implementation.

A conformance claim without a passing run of this suite is not a conformance claim.

---

## Profiles

| Profile | RFC Coverage | Invariants | Designation |
|---|---|---|---|
| **Base** | RFC-ATF-1 | 6 (ATF-INV-001–006) | `ATF-Compliant` |
| **Runtime** | RFC-ATF-1 + RFC-ATF-2 | 14 (+ RGC-INV-001–008) | `ATF-RGC-Compliant` |
| **Forensic** | RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3 | 40 (+ 26 FEI invariants) | `ATF-FEI-Compliant` |

Each profile is strictly additive. ATF-FEI-Compliant requires all 40 invariants.

---

## Quickstart

### Option A — Python (recommended)

```bash
# Install dependencies
pip install pytest jsonschema

# Run all vectors (Base + Runtime + Forensic)
python run_conformance.py --profile ALL

# Run a specific profile
python run_conformance.py --profile RGC

# Run with signed result output
python run_conformance.py --profile ALL --output CONFORMANCE_RESULT.json
```

### Option B — Docker (zero local dependencies)

```bash
docker build -t atf-conformance-suite .
docker run --rm atf-conformance-suite --profile ALL
```

### Option C — Single vector verification

```bash
python run_conformance.py --vector V-ATF-001-P
```

---

## Result Format

Every run produces a machine-readable result. The result is itself a governance artifact — structured identically to an ATF receipt, with a SHA-256 integrity hash and optional PQC signature.

```json
{
  "result_id": "ATFCR-<16HEX>",
  "suite_version": "1.0.0",
  "profile": "ATF-RGC-Compliant",
  "rfc_coverage": ["RFC-ATF-1", "RFC-ATF-2"],
  "invariants_evaluated": 14,
  "run_timestamp": "2026-05-16T14:00:00Z",
  "summary": {
    "total": 28,
    "passed": 28,
    "failed": 0,
    "skipped": 0
  },
  "verdict": "PASS",
  "vectors": [...],
  "result_hash": "sha256:...",
  "pqc_signature": "optional — present when --sign flag is used"
}
```

A result with `"verdict": "PASS"` and zero failures is the prerequisite for declaring conformance.

---

## Architecture

```
atf-conformance-suite/
├── run_conformance.py          # Standalone harness — no OMNIX dependency
├── Dockerfile                  # Zero-dependency containerised execution
├── vectors/
│   └── complete_vectors.json   # All 80+ test vectors, all 40 invariants
├── schema/
│   └── conformance_result.schema.json
├── profiles/
│   ├── ATF-Compliant.json
│   ├── ATF-RGC-Compliant.json
│   └── ATF-FEI-Compliant.json
└── README.md
```

### Invariant Checker Design

Each invariant maps to a dedicated check function. Functions are self-contained: they receive a record dict and return `(verdict, reason_code, detail)`. No external calls, no I/O, no platform state.

```python
def check_atf_inv_001(record: dict) -> CheckResult:
    """ATF-INV-001: Monotonic Authority Reduction (MAR)
    RFC-ATF-1 §7.1 — granted ≤ delegator
    """
    granted = record.get("authority_budget_granted")
    delegator = record.get("authority_budget_delegator")
    if granted is None or delegator is None:
        return FAIL("FIELD_MISSING", "authority_budget_granted or authority_budget_delegator absent")
    if granted > delegator:
        return FAIL("MAR_VIOLATION", f"granted={granted} > delegator={delegator}")
    return PASS()
```

### Independence Guarantee

The suite MUST NOT import, call, or reference the OMNIX reference implementation. The conformance harness verifies the invariant semantics as specified in the RFC documents. This is a design constraint, not a recommendation.

---

## Test Vectors

Vectors are defined in `vectors/complete_vectors.json`. Each vector has:

```json
{
  "id": "V-ATF-001-N",
  "profile": "ATF-Compliant",
  "invariant": "ATF-INV-001",
  "kind": "negative",
  "description": "MAR violation: granted budget exceeds delegator",
  "rfc_ref": "RFC-ATF-1 §7.1",
  "input": { ... },
  "expected": {
    "verdict": "FAIL",
    "reason_code": "MAR_VIOLATION"
  }
}
```

**Vector coverage:**

| Family | Invariants | Positive | Negative | Total |
|---|---|---|---|---|
| ATF-INV (RFC-ATF-1) | 6 | 12 | 12 | 24 |
| RGC-INV (RFC-ATF-2) | 8 | 8 | 8 | 16 |
| GPIL-INV (RFC-ATF-3) | 3 | 3 | 3 | 6 |
| ELR-INV (RFC-ATF-3) | 4 | 4 | 4 | 8 |
| EAP-INV (RFC-ATF-3) | 7 | 7 | 7 | 14 |
| OEP-INV (RFC-ATF-3) | 6 | 6 | 6 | 12 |
| FEA-INV (RFC-ATF-3) | 5 | 5 | 5 | 10 |
| FVP-INV (RFC-ATF-3) | 1 | 1 | 1 | 2 |
| **Total** | **40** | **46** | **46** | **92** |

---

## Declaring Conformance

After a passing run:

1. Save your result JSON: `python run_conformance.py --profile ALL --output result.json`
2. Open a Pull Request to [IMPLEMENTATIONS.md](../IMPLEMENTATIONS.md) with:
   - Implementation name and language
   - PQC library used (ML-DSA-65 / Dilithium-3)
   - Link to your CI run
   - Your `result.json` attached or linked
3. The PR is merged once the result is verified

**The conformance designation belongs to the result, not to the implementation.** Implementations may claim conformance for specific versions against specific suite versions.

---

## Conformance Badges

```markdown
![ATF-Compliant](https://img.shields.io/badge/ATF--Compliant-v1.0-0066cc?style=flat-square&logo=data:image/svg+xml;base64,)
![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-v1.0-0044aa?style=flat-square)
![ATF-FEI-Compliant](https://img.shields.io/badge/ATF--FEI--Compliant-v1.0-002288?style=flat-square)
```

Badges MUST link to a verifiable CI run or stored result JSON. Unverified badge usage is a protocol violation per CONFORMANCE.md §4.

---

## Protocol References

| Document | Version | DOI / SSRN |
|---|---|---|
| RFC-ATF-1: Agent Trust Fabric | 1.0.0 | [doi.org/10.5281/zenodo.20155016](https://doi.org/10.5281/zenodo.20155016) |
| RFC-ATF-2: Runtime Governance Continuity | 1.0.0 | [SSRN 6763978](https://ssrn.com/abstract=6763978) · DOI pending |
| RFC-ATF-3: Forensic Evidence Infrastructure | 1.0.0 | DOI pending |

**Suite version:** 1.0.0  
**Author:** Harold Nunes — OMNIX QUANTUM LTD  
**License:** Creative Commons Attribution 4.0  
**Contact:** standards@omnixquantum.com
