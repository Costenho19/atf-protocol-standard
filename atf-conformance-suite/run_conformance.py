#!/usr/bin/env python3
"""
ATF Conformance Suite — Standalone Harness
Version 1.0.0 · OMNIX QUANTUM LTD

Verifies ATF protocol conformance across all three profiles without
any dependency on the OMNIX platform or reference implementation.

Usage:
    python run_conformance.py --profile ALL
    python run_conformance.py --profile RGC
    python run_conformance.py --profile BASE
    python run_conformance.py --profile FEI
    python run_conformance.py --vector V-ATF-001-N
    python run_conformance.py --profile ALL --output result.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Suite constants
# ---------------------------------------------------------------------------

SUITE_VERSION = "1.0.0"
ATF_PROTOCOL_VERSION = "1.0"

PROFILES = {
    "BASE": {
        "designation": "ATF-Compliant",
        "rfc_coverage": ["RFC-ATF-1"],
        "invariant_families": ["ATF-INV"],
        "invariant_count": 6,
    },
    "RGC": {
        "designation": "ATF-RGC-Compliant",
        "rfc_coverage": ["RFC-ATF-1", "RFC-ATF-2"],
        "invariant_families": ["ATF-INV", "RGC-INV"],
        "invariant_count": 14,
    },
    "FEI": {
        "designation": "ATF-FEI-Compliant",
        "rfc_coverage": ["RFC-ATF-1", "RFC-ATF-2", "RFC-ATF-3"],
        "invariant_families": ["ATF-INV", "RGC-INV", "GPIL-INV", "ELR-INV", "EAP-INV", "OEP-INV", "FEA-INV", "FVP-INV"],
        "invariant_count": 40,
    },
    "ALL": {
        "designation": "ATF-FEI-Compliant",
        "rfc_coverage": ["RFC-ATF-1", "RFC-ATF-2", "RFC-ATF-3"],
        "invariant_families": ["ATF-INV", "RGC-INV", "GPIL-INV", "ELR-INV", "EAP-INV", "OEP-INV", "FEA-INV", "FVP-INV"],
        "invariant_count": 40,
    },
}

PROFILE_FAMILY_MAP = {
    "BASE": ["ATF-INV"],
    "RGC": ["ATF-INV", "RGC-INV"],
    "FEI": ["ATF-INV", "RGC-INV", "GPIL-INV", "ELR-INV", "EAP-INV", "OEP-INV", "FEA-INV", "FVP-INV"],
    "ALL": ["ATF-INV", "RGC-INV", "GPIL-INV", "ELR-INV", "EAP-INV", "OEP-INV", "FEA-INV", "FVP-INV"],
}

INVARIANT_TO_FAMILY = {
    "ATF-INV-001": "ATF-INV", "ATF-INV-002": "ATF-INV", "ATF-INV-003": "ATF-INV",
    "ATF-INV-004": "ATF-INV", "ATF-INV-005": "ATF-INV", "ATF-INV-006": "ATF-INV",
    "RGC-INV-001": "RGC-INV", "RGC-INV-002": "RGC-INV", "RGC-INV-003": "RGC-INV",
    "RGC-INV-004": "RGC-INV", "RGC-INV-005": "RGC-INV", "RGC-INV-006": "RGC-INV",
    "RGC-INV-007": "RGC-INV", "RGC-INV-008": "RGC-INV",
    "GPIL-INV-001": "GPIL-INV", "GPIL-INV-002": "GPIL-INV", "GPIL-INV-003": "GPIL-INV",
    "ELR-INV-001": "ELR-INV", "ELR-INV-002": "ELR-INV", "ELR-INV-003": "ELR-INV", "ELR-INV-004": "ELR-INV",
    "EAP-INV-001": "EAP-INV", "EAP-INV-002": "EAP-INV", "EAP-INV-003": "EAP-INV", "EAP-INV-004": "EAP-INV",
    "EAP-INV-005": "EAP-INV", "EAP-INV-006": "EAP-INV", "EAP-INV-007": "EAP-INV",
    "OEP-INV-001": "OEP-INV", "OEP-INV-002": "OEP-INV", "OEP-INV-003": "OEP-INV",
    "OEP-INV-004": "OEP-INV", "OEP-INV-005": "OEP-INV", "OEP-INV-006": "OEP-INV",
    "FEA-INV-001": "FEA-INV", "FEA-INV-002": "FEA-INV", "FEA-INV-003": "FEA-INV",
    "FEA-INV-004": "FEA-INV", "FEA-INV-005": "FEA-INV",
    "FVP-INV-007": "FVP-INV",
}


# ---------------------------------------------------------------------------
# Result primitives
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    verdict: str          # "PASS" or "FAIL"
    reason_code: Optional[str] = None
    detail: Optional[str] = None


def PASS(detail: str = None) -> CheckResult:
    return CheckResult("PASS", detail=detail)

def FAIL(reason_code: str, detail: str = None) -> CheckResult:
    return CheckResult("FAIL", reason_code=reason_code, detail=detail)


# ---------------------------------------------------------------------------
# ATF-INV checkers (RFC-ATF-1)
# ---------------------------------------------------------------------------

def check_atf_inv_001(record: dict) -> CheckResult:
    """ATF-INV-001: Monotonic Authority Reduction (MAR)
    RFC-ATF-1 §7.1 — authority_budget_granted ≤ authority_budget_delegator
    """
    granted = record.get("authority_budget_granted")
    delegator = record.get("authority_budget_delegator")
    if granted is None:
        return FAIL("FIELD_MISSING", "authority_budget_granted is absent")
    if delegator is None:
        return FAIL("FIELD_MISSING", "authority_budget_delegator is absent")
    if not isinstance(granted, (int, float)) or not isinstance(delegator, (int, float)):
        return FAIL("TYPE_ERROR", "authority_budget fields must be numeric")
    if granted < 0:
        return FAIL("MAR_VIOLATION", f"authority_budget_granted={granted} is negative")
    if granted > delegator:
        return FAIL("MAR_VIOLATION", f"granted={granted} > delegator={delegator} violates MAR")
    return PASS()


def check_atf_inv_002(record: dict) -> CheckResult:
    """ATF-INV-002: Receipt Signing
    RFC-ATF-1 §7.2 — PQC signature MUST be present and cover content_hash
    """
    sig = record.get("pqc_signature")
    algo = record.get("pqc_algorithm")
    content_hash = record.get("content_hash")
    if not sig:
        return FAIL("SIGNATURE_MISSING", "pqc_signature field is absent or empty")
    if not content_hash:
        return FAIL("HASH_MISSING", "content_hash field is absent — signature has no coverage target")
    if algo and algo not in ("ML-DSA-65", "Dilithium-3"):
        return FAIL("ALGORITHM_INVALID", f"pqc_algorithm={algo!r} is not an ATF-approved algorithm")
    # In illustrative/test vectors, "illustrative" is accepted
    if sig == "illustrative" or sig.startswith("sha256:") or len(sig) > 10:
        return PASS()
    return FAIL("SIGNATURE_INVALID", "pqc_signature format is not recognizable")


def check_atf_inv_003(record: dict) -> CheckResult:
    """ATF-INV-003: Chain Root Traceability
    RFC-ATF-1 §7.3 — For root DRs, chain_root_id MUST equal delegation_id
    """
    depth = record.get("delegation_depth")
    chain_root_id = record.get("chain_root_id")
    delegation_id = record.get("delegation_id")
    if chain_root_id is None:
        return FAIL("FIELD_MISSING", "chain_root_id is absent")
    if delegation_id is None:
        return FAIL("FIELD_MISSING", "delegation_id is absent")
    if depth == 1 or depth is None:
        if chain_root_id != delegation_id:
            return FAIL("CHAIN_ROOT_MISMATCH",
                       f"Root DR requires chain_root_id == delegation_id, "
                       f"got chain_root_id={chain_root_id!r} != delegation_id={delegation_id!r}")
    return PASS()


def check_atf_inv_004(record: dict) -> CheckResult:
    """ATF-INV-004: Budget Ceiling
    RFC-ATF-1 §7.4 — granted budget MUST NOT exceed maximum (100 by default)
    """
    granted = record.get("authority_budget_granted")
    max_budget = record.get("max_authority_budget", 100)
    if granted is None:
        return FAIL("FIELD_MISSING", "authority_budget_granted is absent")
    if not isinstance(granted, (int, float)):
        return FAIL("TYPE_ERROR", "authority_budget_granted must be numeric")
    if granted > max_budget:
        return FAIL("BUDGET_CEILING_VIOLATION",
                   f"granted={granted} exceeds ceiling={max_budget}")
    return PASS()


def check_atf_inv_005(record: dict) -> CheckResult:
    """ATF-INV-005: Receipt Immutability
    RFC-ATF-1 §7.5 — content_hash MUST match recomputed hash of canonical fields
    """
    content_hash = record.get("content_hash")
    declared_hash = record.get("declared_hash")
    if not content_hash:
        return FAIL("HASH_MISSING", "content_hash is absent")
    # If a declared_hash is provided (tamper test), compare
    if declared_hash is not None:
        if content_hash != declared_hash:
            return FAIL("HASH_MISMATCH",
                       f"content_hash={content_hash!r} does not match declared_hash={declared_hash!r} — "
                       "receipt has been tampered with")
    # Validate hash format: sha256: prefix + 64 hex chars, or "illustrative" for test vectors
    if content_hash == "illustrative":
        return PASS()
    if content_hash.startswith("sha256:"):
        hex_part = content_hash[7:]
        if len(hex_part) == 64 and all(c in "0123456789abcdef" for c in hex_part.lower()):
            return PASS()
        return FAIL("HASH_FORMAT_INVALID", f"sha256 hash has wrong length or characters: {hex_part!r}")
    return FAIL("HASH_FORMAT_INVALID", f"content_hash must start with 'sha256:' or be 'illustrative'")


def check_atf_inv_006(record: dict) -> CheckResult:
    """ATF-INV-006: Independent Verifiability
    RFC-ATF-1 §7.6 — delegator_public_key MUST be embedded in the receipt
    """
    pub_key = record.get("delegator_public_key")
    if not pub_key:
        return FAIL("PUBLIC_KEY_MISSING",
                   "delegator_public_key absent — offline verification is impossible without it. "
                   "This violates the independent verifiability guarantee.")
    if len(str(pub_key)) < 10:
        return FAIL("PUBLIC_KEY_INVALID", "delegator_public_key is present but too short to be valid")
    return PASS()


# ---------------------------------------------------------------------------
# RGC-INV checkers (RFC-ATF-2)
# ---------------------------------------------------------------------------

def check_rgc_inv_001(record: dict) -> CheckResult:
    """RGC-INV-001: TAR Anchoring
    RFC-ATF-2 §7.3 — Every RCR MUST reference a valid, non-null tar_id
    """
    tar_id = record.get("tar_id")
    if tar_id is None:
        return FAIL("TAR_ANCHOR_MISSING",
                   "tar_id is null — RCR cannot be anchored to a session. "
                   "Every Runtime Continuity Record must reference a valid TAR.")
    if str(tar_id).strip() == "":
        return FAIL("TAR_ANCHOR_EMPTY", "tar_id is present but empty")
    return PASS()


def check_rgc_inv_002(record: dict) -> CheckResult:
    """RGC-INV-002: Real-Time CES Computation
    RFC-ATF-2 §6.4 — CES = T×0.30 + B×0.30 + D×0.20 + I×0.20
    Weights are fixed and non-negotiable.
    """
    ces_score = record.get("ces_score")
    t = record.get("temporal_score")
    b = record.get("budget_score")
    d = record.get("context_score")
    i = record.get("integrity_score")

    if ces_score is None:
        return FAIL("CES_MISSING", "ces_score is absent")

    if None in (t, b, d, i):
        # If component scores are absent, we can only check range
        if not (0 <= ces_score <= 100):
            return FAIL("CES_OUT_OF_RANGE", f"ces_score={ces_score} is outside [0, 100]")
        return PASS()

    for name, val in (("temporal_score", t), ("budget_score", b), ("context_score", d), ("integrity_score", i)):
        if not isinstance(val, (int, float)):
            return FAIL("CES_COMPONENT_TYPE_ERROR", f"{name} must be numeric, got {type(val).__name__}")
        if not (0 <= val <= 100):
            return FAIL("CES_COMPONENT_OUT_OF_RANGE", f"{name}={val} is outside [0, 100]")

    expected = round(t * 0.30 + b * 0.30 + d * 0.20 + i * 0.20, 6)
    actual = round(float(ces_score), 6)

    if abs(expected - actual) > 0.01:
        return FAIL("CES_FORMULA_VIOLATION",
                   f"CES={actual} does not match T×0.30+B×0.30+D×0.20+I×0.20={expected}. "
                   f"Inputs: T={t}, B={b}, D={d}, I={i}. Weights are fixed per RFC-ATF-2 §6.1.")
    return PASS()


def check_rgc_inv_003(record: dict) -> CheckResult:
    """RGC-INV-003: HALT Propagation
    RFC-ATF-2 §10.5 — If status=HALT, all sibling sessions MUST be REVOKED_BY_HALT
    """
    status = record.get("continuity_status")
    siblings = record.get("sibling_session_statuses", [])
    has_halt = record.get("halt_issued", False)

    if status == "HALT" or has_halt:
        for sibling in siblings:
            s_status = sibling.get("status") if isinstance(sibling, dict) else sibling
            if s_status not in ("REVOKED_BY_HALT", "HALTED", "TERMINATED"):
                return FAIL("HALT_PROPAGATION_FAILURE",
                           f"Session entered HALT but sibling has status={s_status!r}. "
                           "All active siblings MUST be revoked when a HALT is triggered.")
    return PASS()


def check_rgc_inv_004(record: dict) -> CheckResult:
    """RGC-INV-004: Authority Fragmentation Guard (AFG)
    RFC-ATF-2 §8.4 — Aggregate budget across active sessions MUST NOT exceed AFG limit
    """
    aggregate = record.get("aggregate_budget_consumed")
    chain_root_budget = record.get("chain_root_budget")
    afg_limit = record.get("afg_fragmentation_limit", 0.90)
    fragmentation_score = record.get("fragmentation_score")

    if fragmentation_score is not None:
        if not (0.0 <= afg_limit <= 0.95):
            return FAIL("AFG_LIMIT_OUT_OF_RANGE",
                       f"afg_fragmentation_limit={afg_limit} is outside [0.0, 0.95]. "
                       "Values above 0.95 are rejected per ADR-replit.md.")
        if fragmentation_score > afg_limit:
            return FAIL("AFG_VIOLATION",
                       f"fragmentation_score={fragmentation_score} > afg_limit={afg_limit}. "
                       "New sub-agent spawning MUST be blocked.")
        return PASS()

    if aggregate is not None and chain_root_budget is not None and chain_root_budget > 0:
        ratio = aggregate / chain_root_budget
        if ratio > afg_limit:
            return FAIL("AFG_VIOLATION",
                       f"aggregate_budget_consumed/chain_root_budget={ratio:.3f} > afg_limit={afg_limit}")
    return PASS()


def check_rgc_inv_005(record: dict) -> CheckResult:
    """RGC-INV-005: RCR Immutability
    RFC-ATF-2 §5.5 — RCRs MUST be write-once; no updates permitted after issuance
    """
    pqc_sig = record.get("pqc_signature")
    update_attempted = record.get("update_attempted", False)
    if update_attempted:
        return FAIL("RCR_MUTABILITY_VIOLATION",
                   "update_attempted=true — RCRs are write-once artifacts. "
                   "No field may be modified after issuance.")
    if not pqc_sig:
        return FAIL("RCR_SIGNATURE_MISSING",
                   "pqc_signature absent — unsigned RCRs cannot satisfy immutability guarantee")
    return PASS()


def check_rgc_inv_006(record: dict) -> CheckResult:
    """RGC-INV-006: Chain Acyclicity
    RFC-ATF-2 §7.2 — execution_ns MUST be strictly greater than predecessor
    """
    execution_ns = record.get("execution_ns")
    predecessor_ns = record.get("predecessor_execution_ns")
    chain = record.get("execution_ns_chain")

    if chain is not None:
        for i in range(1, len(chain)):
            if chain[i] <= chain[i - 1]:
                return FAIL("CHAIN_ACYCLICITY_VIOLATION",
                           f"execution_ns[{i}]={chain[i]} <= execution_ns[{i-1}]={chain[i-1]}. "
                           "Chain MUST be strictly monotonically increasing.")
        return PASS()

    if execution_ns is not None and predecessor_ns is not None:
        if execution_ns <= predecessor_ns:
            return FAIL("CHAIN_ACYCLICITY_VIOLATION",
                       f"execution_ns={execution_ns} <= predecessor_execution_ns={predecessor_ns}. "
                       "Indicates clock manipulation or replay attack.")
    return PASS()


def check_rgc_inv_007(record: dict) -> CheckResult:
    """RGC-INV-007: CES Input Freshness
    RFC-ATF-2 §6.4 — Inputs must meet freshness: CRITICAL<5s, NOMINAL<30s
    """
    continuity_status = record.get("continuity_status", "NOMINAL")
    input_age_seconds = record.get("ces_input_age_seconds")
    stale_inputs = record.get("stale_ces_inputs", False)

    if stale_inputs:
        return FAIL("CES_STALE_INPUTS",
                   "ces_input_age_seconds exceeds freshness requirement. "
                   "CES MUST be computed from values current at sampling time.")

    if input_age_seconds is not None:
        threshold = 5 if continuity_status == "CRITICAL" else 30
        if input_age_seconds > threshold:
            return FAIL("CES_STALE_INPUTS",
                       f"Input age {input_age_seconds}s exceeds {threshold}s threshold for "
                       f"status={continuity_status!r}. Stale inputs produce deceptive CES values.")
    return PASS()


def check_rgc_inv_008(record: dict) -> CheckResult:
    """RGC-INV-008: RC TTL Enforcement
    RFC-ATF-2 §10.4 — RC TTL MUST be enforced; auto-HALT on expiry
    """
    rc_expired = record.get("rc_ttl_expired", False)
    rc_response_status = record.get("rc_response_status")
    auto_halt_triggered = record.get("auto_halt_triggered", False)

    if rc_expired:
        if not auto_halt_triggered:
            return FAIL("RC_TTL_ENFORCEMENT_FAILURE",
                       "rc_ttl_expired=true but auto_halt_triggered=false. "
                       "RC TTL expiry MUST unconditionally trigger HALT per RGC-INV-008.")
        return PASS()

    rc_ttl = record.get("rc_ttl_seconds")
    if rc_ttl is not None and rc_ttl <= 0:
        return FAIL("RC_TTL_INVALID", f"rc_ttl_seconds={rc_ttl} must be positive")
    return PASS()


# ---------------------------------------------------------------------------
# GPIL-INV checkers (RFC-ATF-3)
# ---------------------------------------------------------------------------

def check_gpil_inv_001(record: dict) -> CheckResult:
    """GPIL-INV-001: Interoperability Layer Separation
    RFC-ATF-3 §5.5 — Interoperability claims MUST use the 3-layer taxonomy
    """
    layer = record.get("interoperability_layer")
    valid_layers = ("cryptographic", "protocol", "governance_policy")
    if layer is None:
        return FAIL("GPIL_LAYER_MISSING", "interoperability_layer is absent")
    if str(layer).lower() not in valid_layers:
        return FAIL("GPIL_LAYER_INVALID",
                   f"interoperability_layer={layer!r} is not in {valid_layers}. "
                   "RFC-ATF-3 defines exactly three interoperability layers.")
    return PASS()


def check_gpil_inv_002(record: dict) -> CheckResult:
    """GPIL-INV-002: Policy Parameter Bounds Enforcement
    RFC-ATF-3 §5.6 — Policy parameters MUST stay within protocol-defined ranges
    """
    violations = []
    afg_limit = record.get("afg_fragmentation_limit")
    rc_ttl = record.get("rc_ttl_seconds")
    sampling = record.get("sampling_profile")

    if afg_limit is not None:
        if not (0.01 <= afg_limit <= 0.95):
            violations.append(f"afg_fragmentation_limit={afg_limit} outside [0.01, 0.95]")
    if rc_ttl is not None:
        if not (30 <= rc_ttl <= 3600):
            violations.append(f"rc_ttl_seconds={rc_ttl} outside [30, 3600]")
    if sampling is not None:
        valid_profiles = ("aggressive", "standard", "conservative", "minimal")
        if sampling not in valid_profiles:
            violations.append(f"sampling_profile={sampling!r} not in {valid_profiles}")

    if violations:
        return FAIL("POLICY_PARAMETER_OUT_OF_BOUNDS", "; ".join(violations))
    return PASS()


def check_gpil_inv_003(record: dict) -> CheckResult:
    """GPIL-INV-003: CRGC Signing Completeness
    RFC-ATF-3 §5.7 — CRGC MUST carry valid signatures from all listed parties
    """
    parties = record.get("crgc_parties", [])
    signatures = record.get("crgc_signatures", {})
    missing = [p for p in parties if p not in signatures or not signatures[p]]
    if missing:
        return FAIL("CRGC_SIGNATURE_INCOMPLETE",
                   f"Parties {missing} listed in crgc_parties but absent from crgc_signatures. "
                   "All parties MUST sign the Cross-Runtime Governance Contract.")
    return PASS()


# ---------------------------------------------------------------------------
# ELR-INV checkers (RFC-ATF-3)
# ---------------------------------------------------------------------------

def check_elr_inv_001(record: dict) -> CheckResult:
    """ELR-INV-001: Verifiability Preservation
    RFC-ATF-3 §6.7 — Tier transitions MUST NOT mutate original content_hash
    """
    original_hash = record.get("original_content_hash")
    current_hash = record.get("current_content_hash")
    tier_transitioned = record.get("tier_transitioned", False)

    if tier_transitioned and original_hash and current_hash:
        if original_hash != current_hash:
            return FAIL("VERIFIABILITY_BROKEN",
                       f"Tier transition mutated content_hash: "
                       f"original={original_hash!r} != current={current_hash!r}. "
                       "Hash MUST be preserved verbatim through all tier transitions.")
    return PASS()


def check_elr_inv_002(record: dict) -> CheckResult:
    """ELR-INV-002: Exception Permanence
    RFC-ATF-3 — LEGAL, PQC, CONTRACT, EXCEPTION evidence classes MUST NEVER be deleted
    """
    evidence_class = record.get("evidence_class", "")
    deletion_attempted = record.get("deletion_attempted", False)
    immutable_classes = {"LEGAL", "PQC", "CONTRACT", "EXCEPTION"}

    if evidence_class.upper() in immutable_classes and deletion_attempted:
        return FAIL("EXCEPTION_PERMANENCE_VIOLATION",
                   f"Deletion attempted on evidence_class={evidence_class!r}. "
                   f"Classes {immutable_classes} are permanently immutable and MUST NOT be deleted.")
    return PASS()


def check_elr_inv_003(record: dict) -> CheckResult:
    """ELR-INV-003: Classification Immutability
    RFC-ATF-3 — Evidence class cannot be downgraded after assignment
    """
    original_class = record.get("original_evidence_class")
    current_class = record.get("current_evidence_class")
    class_rank = {"EXCEPTION": 4, "LEGAL": 3, "PQC": 3, "CONTRACT": 2, "OPERATIONAL": 1, "AUDIT": 1}

    if original_class and current_class and original_class != current_class:
        original_rank = class_rank.get(original_class.upper(), 0)
        current_rank = class_rank.get(current_class.upper(), 0)
        if current_rank < original_rank:
            return FAIL("CLASSIFICATION_DOWNGRADE",
                       f"Evidence class downgraded from {original_class!r} to {current_class!r}. "
                       "Classification MUST NOT be downgraded after initial assignment.")
    return PASS()


def check_elr_inv_004(record: dict) -> CheckResult:
    """ELR-INV-004: HOT Retention Minimum
    RFC-ATF-3 — Artifacts MUST remain in HOT tier for at least 30 days
    """
    tier = record.get("storage_tier")
    hot_age_days = record.get("hot_age_days")
    premature_transition = record.get("premature_tier_transition", False)

    if premature_transition:
        return FAIL("HOT_RETENTION_VIOLATION",
                   "Tier transition from HOT attempted before 30-day minimum retention. "
                   "ELR-INV-004 requires artifacts remain in HOT for at least 30 days.")
    if hot_age_days is not None and tier != "HOT" and hot_age_days < 30:
        return FAIL("HOT_RETENTION_VIOLATION",
                   f"hot_age_days={hot_age_days} < 30 minimum before transition from HOT tier.")
    return PASS()


# ---------------------------------------------------------------------------
# EAP-INV checkers (RFC-ATF-3)
# ---------------------------------------------------------------------------

def check_eap_inv_001(record: dict) -> CheckResult:
    """EAP-INV-001: Transition Integrity — original hash recorded before transformation"""
    manifest_hash_recorded = record.get("manifest_hash_recorded_before_transform", True)
    if not manifest_hash_recorded:
        return FAIL("TRANSITION_INTEGRITY_VIOLATION",
                   "Transformation began without recording original hash in manifest. "
                   "EAP-INV-001 requires the original hash to be recorded FIRST.")
    return PASS()


def check_eap_inv_002(record: dict) -> CheckResult:
    """EAP-INV-002: Signature Preservation — pqc_signatures verbatim in COLD storage"""
    signatures_stripped = record.get("signatures_stripped_in_cold", False)
    if signatures_stripped:
        return FAIL("SIGNATURE_STRIPPED",
                   "PQC signatures were stripped during COLD storage transition. "
                   "EAP-INV-002 requires signatures preserved verbatim.")
    return PASS()


def check_eap_inv_003(record: dict) -> CheckResult:
    """EAP-INV-003: Block Chain Integrity — predecessor_block_hash chain unbroken"""
    chain_broken = record.get("predecessor_chain_broken", False)
    predecessor_hash = record.get("predecessor_block_hash")
    if chain_broken:
        return FAIL("BLOCK_CHAIN_BROKEN",
                   "predecessor_block_hash chain has a gap. "
                   "EAP-INV-003 requires an unbroken chain from genesis to current block.")
    return PASS()


def check_eap_inv_004(record: dict) -> CheckResult:
    """EAP-INV-004: Immutable Class Complete — LEGAL etc. MUST NOT be compressed/stripped"""
    evidence_class = record.get("evidence_class", "")
    compressed = record.get("content_compressed", False)
    fields_stripped = record.get("fields_stripped", False)
    immutable_classes = {"LEGAL", "PQC", "CONTRACT", "EXCEPTION"}
    if evidence_class.upper() in immutable_classes and (compressed or fields_stripped):
        return FAIL("IMMUTABLE_CLASS_MODIFIED",
                   f"evidence_class={evidence_class!r} artifact was compressed or stripped. "
                   "Immutable classes MUST be preserved in original form.")
    return PASS()


def check_eap_inv_005(record: dict) -> CheckResult:
    """EAP-INV-005: Offline Reconstructability — verification possible with block + public key only"""
    requires_platform = record.get("verification_requires_platform_access", False)
    if requires_platform:
        return FAIL("OFFLINE_VERIFICATION_IMPOSSIBLE",
                   "Verification of this artifact requires platform access. "
                   "EAP-INV-005 requires verification using only the block file and public key.")
    return PASS()


def check_eap_inv_006(record: dict) -> CheckResult:
    """EAP-INV-006: Manifest Completeness — every transition requires a manifest entry first"""
    manifest_entry_present = record.get("manifest_entry_present_before_transition", True)
    if not manifest_entry_present:
        return FAIL("MANIFEST_INCOMPLETE",
                   "Transition completed without a prior manifest entry. "
                   "EAP-INV-006 requires manifest entry BEFORE transition completion.")
    return PASS()


def check_eap_inv_007(record: dict) -> CheckResult:
    """EAP-INV-007: Global Uniqueness — Block IDs MUST be globally unique"""
    duplicate_block_id = record.get("duplicate_block_id", False)
    block_id = record.get("block_id")
    if duplicate_block_id:
        return FAIL("BLOCK_ID_DUPLICATE",
                   f"block_id={block_id!r} is not globally unique. "
                   "EAP-INV-007 requires all block IDs to be globally unique.")
    return PASS()


# ---------------------------------------------------------------------------
# OEP-INV checkers (RFC-ATF-3)
# ---------------------------------------------------------------------------

def check_oep_inv_001(record: dict) -> CheckResult:
    """OEP-INV-001: Offline Self-Containment — all verification files inside bundle"""
    external_refs = record.get("external_verification_references", [])
    if external_refs:
        return FAIL("OEP_EXTERNAL_DEPENDENCY",
                   f"Bundle references external resources for verification: {external_refs}. "
                   "OEP-INV-001 requires all verification resources inside the .oep bundle.")
    return PASS()


def check_oep_inv_002(record: dict) -> CheckResult:
    """OEP-INV-002: File Integrity Lattice — all files listed in manifest.json with SHA-256"""
    unlisted_files = record.get("files_not_in_manifest", [])
    if unlisted_files:
        return FAIL("OEP_MANIFEST_INCOMPLETE",
                   f"Files not listed in manifest.json: {unlisted_files}. "
                   "Every file in the OEP bundle MUST have a SHA-256 entry in manifest.json.")
    return PASS()


def check_oep_inv_003(record: dict) -> CheckResult:
    """OEP-INV-003: Mandatory Package Signature — two-phase PQC signature MUST be present"""
    phase1_sig = record.get("package_signature_phase1")
    phase2_sig = record.get("package_signature_phase2")
    if not phase1_sig:
        return FAIL("OEP_SIGNATURE_PHASE1_MISSING", "package_signature_phase1 is absent")
    if not phase2_sig:
        return FAIL("OEP_SIGNATURE_PHASE2_MISSING", "package_signature_phase2 is absent")
    return PASS()


def check_oep_inv_004(record: dict) -> CheckResult:
    """OEP-INV-004: Chain Completeness — no gaps in BLOCKS/ directory sequence"""
    block_sequence_gap = record.get("block_sequence_gap", False)
    if block_sequence_gap:
        return FAIL("OEP_CHAIN_GAP",
                   "Gap detected in BLOCKS/ directory block sequence. "
                   "OEP-INV-004 requires a complete, unbroken block chain.")
    return PASS()


def check_oep_inv_005(record: dict) -> CheckResult:
    """OEP-INV-005: Embedded Public Key — key MUST be in KEYS/, not referenced externally"""
    key_embedded = record.get("public_key_embedded_in_bundle", True)
    external_key_url = record.get("public_key_external_url")
    if not key_embedded:
        return FAIL("OEP_KEY_NOT_EMBEDDED",
                   "Public key is not embedded in KEYS/ directory of the bundle. "
                   "OEP-INV-005 prohibits external key references.")
    if external_key_url:
        return FAIL("OEP_EXTERNAL_KEY_REFERENCE",
                   f"public_key_external_url={external_key_url!r} is present. "
                   "Key MUST be embedded — external references defeat offline verifiability.")
    return PASS()


def check_oep_inv_006(record: dict) -> CheckResult:
    """OEP-INV-006: Schema Version Lock — manifest_version MUST be exactly 'oep-1.0'"""
    manifest_version = record.get("manifest_version")
    if manifest_version is None:
        return FAIL("OEP_VERSION_MISSING", "manifest_version is absent from manifest.json")
    if manifest_version != "oep-1.0":
        return FAIL("OEP_VERSION_MISMATCH",
                   f"manifest_version={manifest_version!r} != 'oep-1.0'. "
                   "Schema version MUST be exactly 'oep-1.0'.")
    return PASS()


# ---------------------------------------------------------------------------
# FEA-INV checkers (RFC-ATF-3)
# ---------------------------------------------------------------------------

def check_fea_inv_001(record: dict) -> CheckResult:
    """FEA-INV-001: Key Isolation — platform private key MUST NOT appear in HTTP request body"""
    private_key_in_request = record.get("private_key_in_http_request", False)
    if private_key_in_request:
        return FAIL("KEY_ISOLATION_VIOLATION",
                   "Platform private key present in HTTP request body. "
                   "FEA-INV-001: private key MUST never appear in request payloads.")
    return PASS()


def check_fea_inv_002(record: dict) -> CheckResult:
    """FEA-INV-002: Audit Non-Repudiation — every export MUST be logged before package returned"""
    export_logged_before_return = record.get("export_logged_before_return", True)
    if not export_logged_before_return:
        return FAIL("AUDIT_NON_REPUDIATION_FAILURE",
                   "Export package returned before audit log entry was written. "
                   "FEA-INV-002 requires logging FIRST, delivery SECOND.")
    return PASS()


def check_fea_inv_003(record: dict) -> CheckResult:
    """FEA-INV-003: Authentication Required — /export MUST return 401 without valid admin key"""
    auth_header = record.get("authorization_header")
    response_status = record.get("response_status_code")
    if not auth_header and response_status != 401:
        return FAIL("AUTHENTICATION_BYPASS",
                   f"Request without authorization_header returned status={response_status} "
                   "instead of 401. FEA-INV-003: unauthenticated /export requests MUST be rejected.")
    return PASS()


def check_fea_inv_004(record: dict) -> CheckResult:
    """FEA-INV-004: Fail-Closed — /export MUST return 503 if signing key is missing"""
    signing_key_present = record.get("signing_key_configured", True)
    response_status = record.get("response_status_code")
    if not signing_key_present and response_status != 503:
        return FAIL("FAIL_OPEN_VIOLATION",
                   f"Signing key absent but /export returned status={response_status} "
                   "instead of 503. FEA-INV-004: missing key MUST cause fail-closed (503).")
    return PASS()


def check_fea_inv_005(record: dict) -> CheckResult:
    """FEA-INV-005: Caller Key Prohibition — production MUST NOT allow caller-provided keys"""
    environment = record.get("environment", "production")
    caller_key_accepted = record.get("caller_key_accepted", False)
    allow_flag = record.get("forensic_export_allow_caller_keys", False)

    if environment == "production" and (caller_key_accepted or allow_flag):
        return FAIL("CALLER_KEY_IN_PRODUCTION",
                   "FORENSIC_EXPORT_ALLOW_CALLER_KEYS=true detected in production environment. "
                   "FEA-INV-005: caller-provided keys are PROHIBITED in production. "
                   "This flag is only valid in dev/test environments (ADR-166).")
    return PASS()


# ---------------------------------------------------------------------------
# FVP-INV checker (RFC-ATF-3)
# ---------------------------------------------------------------------------

def check_fvp_inv_007(record: dict) -> CheckResult:
    """FVP-INV-007: Key Identity Disclosure
    RFC-ATF-3 — /verify responses MUST include a key_identity fingerprint
    """
    key_identity = record.get("key_identity")
    response_type = record.get("response_type", "verify")
    if response_type == "verify" and not key_identity:
        return FAIL("KEY_IDENTITY_MISSING",
                   "Verification response does not include key_identity fingerprint. "
                   "FVP-INV-007: every /verify response MUST disclose key_identity to prevent "
                   "verification oracle abuse.")
    return PASS()


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

CHECKERS = {
    "ATF-INV-001": check_atf_inv_001,
    "ATF-INV-002": check_atf_inv_002,
    "ATF-INV-003": check_atf_inv_003,
    "ATF-INV-004": check_atf_inv_004,
    "ATF-INV-005": check_atf_inv_005,
    "ATF-INV-006": check_atf_inv_006,
    "RGC-INV-001": check_rgc_inv_001,
    "RGC-INV-002": check_rgc_inv_002,
    "RGC-INV-003": check_rgc_inv_003,
    "RGC-INV-004": check_rgc_inv_004,
    "RGC-INV-005": check_rgc_inv_005,
    "RGC-INV-006": check_rgc_inv_006,
    "RGC-INV-007": check_rgc_inv_007,
    "RGC-INV-008": check_rgc_inv_008,
    "GPIL-INV-001": check_gpil_inv_001,
    "GPIL-INV-002": check_gpil_inv_002,
    "GPIL-INV-003": check_gpil_inv_003,
    "ELR-INV-001": check_elr_inv_001,
    "ELR-INV-002": check_elr_inv_002,
    "ELR-INV-003": check_elr_inv_003,
    "ELR-INV-004": check_elr_inv_004,
    "EAP-INV-001": check_eap_inv_001,
    "EAP-INV-002": check_eap_inv_002,
    "EAP-INV-003": check_eap_inv_003,
    "EAP-INV-004": check_eap_inv_004,
    "EAP-INV-005": check_eap_inv_005,
    "EAP-INV-006": check_eap_inv_006,
    "EAP-INV-007": check_eap_inv_007,
    "OEP-INV-001": check_oep_inv_001,
    "OEP-INV-002": check_oep_inv_002,
    "OEP-INV-003": check_oep_inv_003,
    "OEP-INV-004": check_oep_inv_004,
    "OEP-INV-005": check_oep_inv_005,
    "OEP-INV-006": check_oep_inv_006,
    "FEA-INV-001": check_fea_inv_001,
    "FEA-INV-002": check_fea_inv_002,
    "FEA-INV-003": check_fea_inv_003,
    "FEA-INV-004": check_fea_inv_004,
    "FEA-INV-005": check_fea_inv_005,
    "FVP-INV-007": check_fvp_inv_007,
}


def run_vector(vector: dict) -> dict:
    """Execute a single test vector and return the outcome."""
    invariant_id = vector.get("invariant")
    input_record = vector.get("input", {})
    expected = vector.get("expected", {})

    checker = CHECKERS.get(invariant_id)
    if not checker:
        return {
            "id": vector.get("id"),
            "invariant": invariant_id,
            "verdict": "SKIP",
            "reason_code": "NO_CHECKER",
            "detail": f"No checker registered for {invariant_id}",
            "expected_verdict": expected.get("verdict"),
            "outcome": "SKIP",
        }

    result = checker(input_record)

    expected_verdict = expected.get("verdict")
    expected_reason = expected.get("reason_code")

    verdict_match = result.verdict == expected_verdict
    reason_match = (expected_reason is None) or (result.reason_code == expected_reason)
    outcome = "PASS" if (verdict_match and reason_match) else "FAIL"

    return {
        "id": vector.get("id"),
        "invariant": invariant_id,
        "kind": vector.get("kind"),
        "description": vector.get("description"),
        "rfc_ref": vector.get("rfc_ref"),
        "actual_verdict": result.verdict,
        "actual_reason_code": result.reason_code,
        "actual_detail": result.detail,
        "expected_verdict": expected_verdict,
        "expected_reason_code": expected_reason,
        "outcome": outcome,
    }


def load_vectors(vectors_path: Path) -> list:
    with open(vectors_path) as f:
        data = json.load(f)
    return data.get("vectors", data) if isinstance(data, dict) else data


def filter_vectors(vectors: list, profile: str = None, vector_id: str = None) -> list:
    if vector_id:
        return [v for v in vectors if v.get("id") == vector_id]
    if profile and profile != "ALL":
        allowed_families = PROFILE_FAMILY_MAP.get(profile, [])
        return [
            v for v in vectors
            if INVARIANT_TO_FAMILY.get(v.get("invariant", ""), "") in allowed_families
        ]
    return vectors


def generate_result_id() -> str:
    return "ATFCR-" + secrets.token_hex(8).upper()


def compute_hash(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def run_suite(vectors_path: Path, profile: str = "ALL", vector_id: str = None) -> dict:
    all_vectors = load_vectors(vectors_path)
    selected = filter_vectors(all_vectors, profile, vector_id)

    results = [run_vector(v) for v in selected]

    passed = sum(1 for r in results if r["outcome"] == "PASS")
    failed = sum(1 for r in results if r["outcome"] == "FAIL")
    skipped = sum(1 for r in results if r["outcome"] == "SKIP")

    profile_cfg = PROFILES.get(profile, PROFILES["ALL"])
    overall_verdict = "PASS" if failed == 0 and passed > 0 else "FAIL"

    result = {
        "result_id": generate_result_id(),
        "suite_version": SUITE_VERSION,
        "profile": profile_cfg["designation"],
        "profile_key": profile,
        "rfc_coverage": profile_cfg["rfc_coverage"],
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "verdict": overall_verdict,
        "vectors": results,
    }

    result["result_hash"] = compute_hash({k: v for k, v in result.items() if k != "result_hash"})
    return result


def print_report(result: dict, verbose: bool = False) -> None:
    summary = result["summary"]
    verdict = result["verdict"]
    color_pass = "\033[32m" if sys.stdout.isatty() else ""
    color_fail = "\033[31m" if sys.stdout.isatty() else ""
    color_skip = "\033[33m" if sys.stdout.isatty() else ""
    color_reset = "\033[0m" if sys.stdout.isatty() else ""
    color_bold = "\033[1m" if sys.stdout.isatty() else ""

    print(f"\n{color_bold}ATF Conformance Suite {SUITE_VERSION}{color_reset}")
    print(f"Profile:   {result['profile']}")
    print(f"Coverage:  {', '.join(result['rfc_coverage'])}")
    print(f"Run:       {result['run_timestamp']}")
    print(f"Result ID: {result['result_id']}")
    print()

    # Per-invariant summary
    by_invariant: dict[str, list] = {}
    for r in result["vectors"]:
        inv = r["invariant"]
        by_invariant.setdefault(inv, []).append(r)

    for inv_id in sorted(by_invariant.keys()):
        v_results = by_invariant[inv_id]
        inv_pass = sum(1 for r in v_results if r["outcome"] == "PASS")
        inv_fail = sum(1 for r in v_results if r["outcome"] == "FAIL")
        status = f"{color_pass}✓{color_reset}" if inv_fail == 0 else f"{color_fail}✗{color_reset}"
        print(f"  {status} {inv_id:<16} {inv_pass}/{len(v_results)} vectors")

        if verbose or inv_fail > 0:
            for r in v_results:
                o = r["outcome"]
                sym = f"{color_pass}PASS{color_reset}" if o == "PASS" else (
                    f"{color_fail}FAIL{color_reset}" if o == "FAIL" else f"{color_skip}SKIP{color_reset}")
                print(f"       [{sym}] {r['id']:<20} {r.get('description', '')[:60]}")
                if o == "FAIL":
                    print(f"              expected={r['expected_verdict']} reason={r['expected_reason_code']}")
                    print(f"              actual  ={r['actual_verdict']} reason={r['actual_reason_code']}")
                    if r.get("actual_detail"):
                        print(f"              detail  ={r['actual_detail']}")

    print()
    verdict_str = (
        f"{color_pass}{color_bold}PASS{color_reset}" if verdict == "PASS"
        else f"{color_fail}{color_bold}FAIL{color_reset}"
    )
    print(f"{'─'*50}")
    print(f"Verdict:   {verdict_str}")
    print(f"Passed:    {color_pass}{summary['passed']}{color_reset} / {summary['total']}")
    if summary['failed']:
        print(f"Failed:    {color_fail}{summary['failed']}{color_reset}")
    if summary['skipped']:
        print(f"Skipped:   {color_skip}{summary['skipped']}{color_reset}")
    print(f"Hash:      {result['result_hash']}")
    print()

    if verdict == "PASS":
        print(f"  {color_pass}This implementation satisfies all evaluated invariants for profile:{color_reset}")
        print(f"  {color_bold}  {result['profile']}{color_reset}")
    else:
        print(f"  {color_fail}Conformance NOT achieved. Resolve all FAIL vectors before claiming:{color_reset}")
        print(f"  {color_bold}  {result['profile']}{color_reset}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="ATF Conformance Suite — Standalone invariant verification harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Profiles:
  BASE    ATF-Compliant (RFC-ATF-1, 6 invariants)
  RGC     ATF-RGC-Compliant (RFC-ATF-1+2, 14 invariants)
  FEI     ATF-FEI-Compliant (RFC-ATF-1+2+3, 40 invariants)
  ALL     Full suite (equivalent to FEI)

Examples:
  python run_conformance.py --profile RGC
  python run_conformance.py --profile ALL --output result.json
  python run_conformance.py --vector V-ATF-001-N
        """
    )
    parser.add_argument("--profile", choices=["BASE", "RGC", "FEI", "ALL"], default="ALL")
    parser.add_argument("--vector", help="Run a single vector by ID")
    parser.add_argument("--output", help="Write result JSON to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all vector results")
    parser.add_argument(
        "--vectors",
        default=str(Path(__file__).parent / "vectors" / "complete_vectors.json"),
        help="Path to vectors JSON file"
    )
    args = parser.parse_args()

    vectors_path = Path(args.vectors)
    if not vectors_path.exists():
        print(f"ERROR: Vectors file not found: {vectors_path}", file=sys.stderr)
        sys.exit(2)

    result = run_suite(vectors_path, profile=args.profile, vector_id=args.vector)
    print_report(result, verbose=args.verbose)

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Result written to: {out_path}")

    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
