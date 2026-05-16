# ATF Conformance Program — v1.1

The ATF Conformance Program is the primary mechanism by which implementations
of the Agent Trust Fabric protocol declare and evidence their compliance.

**Three profiles — progressively stricter:**

| Profile | RFC Coverage | Invariants | Use Case |
|---|---|---|---|
| `ATF-Compliant` | RFC-ATF-1 | 6 (ATF-INV-001–006) | Basic AI agent delegation |
| `ATF-RGC-Compliant` | RFC-ATF-1 + RFC-ATF-2 | 14 | Long-running agent tasks |
| `ATF-FEI-Compliant` | RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3 | 40 | Forensic / regulatory grade |

---

## ATF Conformance Suite

The **ATF Conformance Suite** (`atf-conformance-suite/`) is the canonical,
standalone verification harness for all 40 ATF invariants.

It requires no OMNIX infrastructure, no external services, and no persistent state.
Any implementation can run it against any ATF-compatible receipt set.

```bash
# Clone and run — no dependencies beyond Python 3.8+
git clone https://github.com/Costenho19/atf-protocol-standard
cd atf-protocol-standard/atf-conformance-suite
python run_conformance.py --profile ALL --output result.json
```

Each run produces a tamper-detectable **ATF Conformance Result (ATFCR)**:

```json
{
  "atfcr_id": "ATFCR-FE46C0F921F6EFE4",
  "profile": "ATF-FEI-Compliant",
  "verdict": "PASS",
  "passed": 86,
  "total": 86,
  "integrity": "sha256:fe6f17e8287f562093018245430b0a4e7055065775f62ea2d3df11a0af719d3d",
  "generated_at": "2026-05-16T21:40:35.474576+00:00"
}
```

The `atfcr_id` and `integrity` hash together form a tamper-detectable
conformance artifact suitable for inclusion in implementation reports,
regulatory submissions, and CI audit logs.

See [`atf-conformance-suite/README.md`](./atf-conformance-suite/README.md) for full documentation.

---

## How to Claim Conformance

> **Self-certification note:** Conformance designations are self-declared by implementers
> based on the test vectors and verification tools provided in this repository.
> No third-party certification body is currently designated. False or unverifiable
> conformance claims may be removed from [IMPLEMENTATIONS.md](./IMPLEMENTATIONS.md)
> at the Editor's discretion.

### Step 1 — Run the ATF Conformance Suite

```bash
git clone https://github.com/Costenho19/atf-protocol-standard
cd atf-protocol-standard/atf-conformance-suite

python run_conformance.py --profile BASE --output result.json   # ATF-Compliant (L1–L3)
python run_conformance.py --profile RGC  --output result.json   # ATF-RGC-Compliant (L1–L4)
python run_conformance.py --profile ALL  --output result.json   # ATF-FEI-Compliant (all 40)
```

All vectors for the target profile must produce verdict `PASS`.
Save `result.json` — it contains the `ATFCR-*` ID required for Step 4.

Alternatively, run the legacy pytest suite:

```bash
pip install pytest pypqc jsonschema
pytest tests/test_conformance_vectors.py -v --tb=short
```

### Step 2 — Run the offline verifier

```bash
python verifier/verify_receipt.py examples/delegation_receipt.json
python verifier/verify_receipt.py examples/runtime_continuity_record.json
```

Both must return `PASS`.

### Step 3 — For `ATF-FEI-Compliant`: verify an OEP package

```bash
python verifier/verify_oep_package.py <your_evidence.zip> --public-key <issuer_pub.b64>
```

Must return `PASS`.

### Step 4 — Produce your Implementation Report

Your report must include:

```json
{
  "implementation": "<name>",
  "version": "<version>",
  "profile": "ATF-Compliant | ATF-RGC-Compliant | ATF-FEI-Compliant",
  "language": "<language>",
  "pqc_library": "<library and version>",
  "invariants_covered": ["ATF-INV-001", "..."],
  "conformance_suite_result": {
    "atfcr_id": "ATFCR-XXXXXXXXXXXXXXXX",
    "verdict": "PASS",
    "passed": 86,
    "total": 86,
    "integrity": "sha256:...",
    "suite_version": "1.0.0"
  },
  "verified_by": "<name or org>",
  "date": "YYYY-MM-DD"
}
```

### Step 5 — Register in IMPLEMENTATIONS.md

Open a Pull Request adding your implementation to
[IMPLEMENTATIONS.md](./IMPLEMENTATIONS.md) with your report linked.

---

## Badge Usage

After completing the above steps, you may use the appropriate badge in your
repository:

```markdown
![ATF-Compliant](https://img.shields.io/badge/ATF--Compliant-RFC--ATF--1-blue?style=flat-square)
![ATF-RGC-Compliant](https://img.shields.io/badge/ATF--RGC--Compliant-RFC--ATF--2-blue?style=flat-square)
![ATF-FEI-Compliant](https://img.shields.io/badge/ATF--FEI--Compliant-RFC--ATF--3-blue?style=flat-square)
```

Badges must link to your Implementation Report or CI run containing the `ATFCR-*` result.
Unverified badge usage is a protocol violation.

---

## Conformance Test Vectors

The canonical vector set is in
[`atf-conformance-suite/vectors/complete_vectors.json`](./atf-conformance-suite/vectors/complete_vectors.json).

Each vector specifies:

| Field | Description |
|---|---|
| `id` | Unique vector ID (e.g. `V-ATF-001-P1`) |
| `profile` | Target conformance profile |
| `invariant` | Invariant under test |
| `kind` | `positive` (must PASS) or `negative` (must FAIL) |
| `description` | Human-readable test description |
| `rfc_ref` | Normative RFC section reference |
| `input` | Receipt JSON or partial receipt |
| `expected.verdict` | `PASS` or `FAIL` |
| `expected.reason_code` | Normative reason code for FAIL cases |

**Test vector counts by invariant family:**

| Family | RFCs | Invariants | Positive | Negative | Total |
|---|---|---|---|---|---|
| ATF | RFC-ATF-1 | ATF-INV-001–006 | 10 | 6 | 16 |
| RGC | RFC-ATF-2 | RGC-INV-001–008 | 12 | 8 | 20 |
| GPIL | RFC-ATF-3 §4 | GPIL-INV-001–003 | 3 | 3 | 6 |
| ELR | RFC-ATF-3 §5 | ELR-INV-001–004 | 4 | 4 | 8 |
| EAP | RFC-ATF-3 §6 | EAP-INV-001–007 | 7 | 7 | 14 |
| OEP | RFC-ATF-3 §7 | OEP-INV-001–006 | 6 | 6 | 12 |
| FEA | RFC-ATF-3 §8 | FEA-INV-001–005 | 5 | 5 | 10 |
| FVP | RFC-ATF-3 §9 | FVP-INV-007 | 1 | 1 | 2 |
| **Total** | **3 RFCs** | **40** | **48** | **40** | **88+** |

> The suite ships 92 total vectors including extended positive cases for
> ATF-INV-001 (4 vectors), ATF-INV-002 (3 vectors), and RGC-INV-002 (4 vectors).

---

## Result Schema

Conformance results are validated against
[`atf-conformance-suite/schema/conformance_result.schema.json`](./atf-conformance-suite/schema/conformance_result.schema.json).

The schema is the normative definition of a valid ATFCR artifact.
Results that do not validate against this schema cannot support
a conformance designation claim.

---

## Determinism Requirement (FVP-INV-007)

Any two conformant verifier implementations, given identical input (same receipt
JSON and same public key), MUST produce identical output: same verdict, same
check results, same reason codes.

This is a hard requirement. Non-deterministic implementations cannot claim
any ATF conformance profile.

The conformance suite explicitly tests this property in vectors
`V-FVP-007-P1` and `V-FVP-007-N1`.

---

## Errata and Vector Updates

Conformance vectors are versioned alongside the protocol.
A vector update that changes expected verdicts constitutes a minor version bump.
Vector additions are patch-level changes.

| Version | Date | Change |
|---|---|---|
| v1.0 | May 2026 | Initial 34-vector suite (RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3 partial) |
| v1.1 | May 2026 | ATF Conformance Suite — 92 vectors, all 40 invariants, ATFCR result format |

---

**Published specifications:**
- RFC-ATF-1: DOI 10.5281/zenodo.20155016
- RFC-ATF-2: DOI 10.5281/zenodo.20241344

*OMNIX QUANTUM LTD · standards@omnixquantum.com · CC BY 4.0*
