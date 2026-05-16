```
Published Standard                                     OMNIX QUANTUM LTD
Category: Standards Track                                    H. Nunes, Ed.
ISSN: pending                                                    May 2026


  RFC-ATF-3: Agent Trust Fabric — Governance Policy Interoperability,
        Evidence Lifecycle, and Forensic Verification Protocol
      Extension to RFC-ATF-1 and RFC-ATF-2 · Version 1.0.0
                   OMNIX QUANTUM Open Standard


Abstract

   This document specifies three coordinated extensions to the Agent
   Trust Fabric (ATF) protocol stack established by RFC-ATF-1 and
   RFC-ATF-2.

   RFC-ATF-1 defined the cryptographic foundation for post-quantum-
   secured agent authority delegation: the Identity Plane, the
   Delegation Plane, and the Verification Plane.  RFC-ATF-2 extended
   that foundation into the runtime dimension: continuous authority
   health monitoring via the Continuity Eligibility Score (CES), the
   Authority Fragmentation Guard (AFG), and the Reauthorization
   Challenge (RC) protocol.

   A governance infrastructure that can delegate authority, monitor it
   continuously at runtime, and halt on degradation still confronts a
   third structural challenge: what happens to the evidence it produces?
   Who is authorized to interpret it across organizational boundaries?
   How does an auditor — without any access to the live platform —
   verify a complete chain of governance custody years later?

   RFC-ATF-3 addresses this challenge across three coordinated
   specifications:

   (1) The Governance Policy Interoperability Layer (GPIL) — a formal
       taxonomy of three interoperability levels (Cryptographic,
       Protocol, and Governance Policy), a Policy Parameter Registry
       defining sovereign parameters within protocol-bounded ranges, and
       a Cross-Runtime Governance Contract (CRGC) mechanism enabling
       multi-party governance alignment without platform lock-in.

   (2) The Evidence Lifecycle & Archive Pipeline (ELP) — eight evidence
       classes mapped to HOT/WARM/COLD retention tiers, four lifecycle
       invariants (ELR-INV-001–004), and a seven-invariant Immutable
       Evidence Archive Pipeline (EAP-INV-001–007) establishing a
       forensic-grade chain of custody from genesis event to permanent
       COLD archive block.

   (3) The Forensic Verification Protocol (FVP) — the OMNIX Evidence
       Package (OEP) format for cryptographically sealed, self-contained
       forensic deliverables; authenticated export governance; and the
       key identity fingerprinting protocol that prevents verification
       oracle abuse.

   RFC-ATF-3 introduces twenty-six new invariants across six families:
   GPIL-INV-001–003, ELR-INV-001–004, EAP-INV-001–007, OEP-INV-001–006,
   FEA-INV-001–005, and FVP-INV-007.  Combined with the fourteen
   invariants of RFC-ATF-1 and RFC-ATF-2, the full ATF invariant stack
   reaches forty formally specified, formally specified constraints.

   An implementation that complies with RFC-ATF-1, RFC-ATF-2, and
   RFC-ATF-3 is designated ATF-FEI-Compliant (Forensic Evidence
   Infrastructure Compliant).


Status of This Memo

   This is an OMNIX QUANTUM Open Standard, published under the
   OMNIX Open Governance License v1.0.  This document extends RFC-ATF-1
   and RFC-ATF-2 and MUST be read in conjunction with both.
   Implementers of RFC-ATF-2 who require multi-runtime governance
   alignment, forensic evidence lifecycle management, or institutional
   forensic deliverables SHOULD adopt RFC-ATF-3 as specified herein.

   Feedback and errata should be submitted to the OMNIX Standards Track
   at standards@omnixquantum.com.

   This document is a product of the OMNIX QUANTUM Standards Working
   Group.  It has been approved for publication by the OMNIX Technical
   Committee.

   Published: May 2026
   DOI: 10.5281/zenodo.20247342
   SSRN: pending


Copyright Notice

   Copyright (c) 2026 OMNIX QUANTUM LTD.  All rights reserved.
   This document may be reproduced for implementation purposes.


Acknowledgements

   This document extends the work established in RFC-ATF-1 and
   RFC-ATF-2.  The foundational interoperability observations that
   motivated the GPIL specification (§5) are formally credited in
   RFC-ATF-2 §21, where they originated.


Table of Contents

    1.  Introduction
    2.  Problem Statement: The Governance Evidence Gap
    3.  Conventions and Terminology
    4.  Architecture: FEI Layer (Layer 5)
        4.1. Position in the ATF Stack
        4.2. Extension Relationships
    5.  Governance Policy Interoperability Layer (GPIL)
        5.1. Three-Layer Interoperability Taxonomy
        5.2. Policy Parameter Registry
        5.3. Cross-Runtime Governance Contracts (CRGC)
        5.4. GPIL Compliance Designations
        5.5. GPIL Invariants
    6.  Evidence Lifecycle Classification (ELR)
        6.1. Evidence Classes
        6.2. Retention Tiers
        6.3. Retention Policy Matrix
        6.4. Shadow Event Reduction Policy
        6.5. RCR Summarization Policy
        6.6. Database Maintenance Policy
        6.7. ELR Invariants
    7.  Immutable Evidence Archive Pipeline (EAP)
        7.1. Pipeline Stage Overview
        7.2. HOT Stage
        7.3. WARM Stage and Transition Manifest
        7.4. COLD Stage: Block Format
        7.5. Block Chaining
        7.6. Offline Verifier Extension
        7.7. Pipeline Trigger Model
        7.8. Evidence Custody Log
        7.9. EAP Invariants
    8.  OMNIX Evidence Package (OEP)
        8.1. Physical Format
        8.2. Directory Structure
        8.3. Package Manifest Schema
        8.4. Two-Phase Package Signing Protocol
        8.5. Independent Verification Procedure
        8.6. Forensic Reconstruction Report
        8.7. OEP Invariants
    9.  Forensic Export Authentication (FEA)
        9.1. Authentication Gate
        9.2. Platform Key Resolution
        9.3. Audit Logging
        9.4. FEA Invariants
   10.  Forensic Verification Protocol (FVP)
        10.1. Key Identity Fingerprinting
        10.2. Distributed Block Sequencing
        10.3. Distributed Rate Limiting
        10.4. Verifier Library Determinism
        10.5. FVP Invariants
   11.  Combined Invariant Summary
   12.  Compliance Designations
        12.1. ATF-FEI-Compliant
        12.2. Compliance Hierarchy
   13.  Implementation Requirements
   14.  Security Considerations
        14.1. Key Identity Inversion Attack
        14.2. Block ID Collision in Distributed Deployments
        14.3. Archive Tampering and Chain Break
        14.4. Package Impersonation
        14.5. Rate Limit Bypass via Auto-Scaling
        14.6. Key Rotation and Public Key Registry
   15.  References
   16.  Appendix A — COLD Block Format Reference
   17.  Appendix B — OEP Directory Structure Reference
   18.  Appendix C — FEI Compliance Checklist


1.  Introduction

   The Agent Trust Fabric protocol stack addresses a problem that every
   regulated autonomous AI infrastructure must eventually solve: not
   just who authorized an agent action, but whether that authorization
   remained valid throughout execution, and whether the evidence of
   both facts is permanently, independently recoverable.

   RFC-ATF-1 answered the first question.  RFC-ATF-2 answered the
   second.  RFC-ATF-3 answers the third.

   The third question has three facets.

   First, the interoperability facet.  As ATF deployments proliferate
   across organizations and cloud environments, two runtimes that are
   each individually RFC-ATF-2-compliant can reach divergent governance
   conclusions from identical signed artifacts — not because either is
   wrong, but because the protocol deliberately leaves certain
   parameters sovereign to each runtime.  Without a formal framework
   for that divergence surface, compliance auditors cannot distinguish
   a policy choice from a protocol violation.  Multi-cloud governance
   contracts cannot be formally specified.  Cross-organizational
   delegation chains cannot declare interoperability guarantees.

   Second, the evidence lifecycle facet.  A runtime governance
   infrastructure continuously produces cryptographically signed,
   legally relevant artifacts: Delegation Receipts, Temporal
   Admissibility Records, Runtime Continuity Records, Continuity
   Escalation Events, and Reauthorization Challenges.  Without a
   formal retention policy, all of these are treated identically —
   stored in the same tables with the same indexes, indefinitely —
   regardless of whether they are irreplaceable legal evidence or
   routine telemetry.  The absence of a lifecycle policy is itself a
   forensic risk: an auditor cannot determine which artifacts are
   permanent, which are summarizable, and which are legally immutable.

   Third, the forensic delivery facet.  Regulated institutions do not
   receive governance evidence as raw database rows.  They require
   self-contained, cryptographically sealed forensic packages that can
   be transmitted via secure channel, stored in a compliance archive,
   presented to a regulator without live platform access, and verified
   by any party with only a standard Python installation years later.
   No such format has existed for the ATF protocol stack.

   RFC-ATF-3 addresses all three facets with a unified, formally
   specified extension that adds Layer 5 — the Forensic Evidence
   Infrastructure (FEI) layer — to the ATF stack.


2.  Problem Statement: The Governance Evidence Gap

   Define the following conditions for a governance evidence artifact A
   produced by an ATF-RGC-Compliant runtime R:

   Independent Cryptographic Verifiability (ICV):
      A is verifiable offline by any party holding the issuer's public
      key, without platform access.  Established by ATF-INV-006
      (RFC-ATF-1) for Delegation Receipts and extended by RFC-ATF-2
      to RCRs, CEEs, and RCs.

   Cross-Runtime Governance Agreement (CRGA):
      Two compliant runtimes R₁ and R₂, presented with the same
      artifact A, reach identical governance conclusions.  ICV does
      not imply CRGA.  Two runtimes can each verify A successfully
      and reach different governance conclusions — legally, because
      policy parameters within RFC-ATF-2's bounds differ.

   Lifecycle-Aware Preservation (LAP):
      An artifact is preserved with a classification that correctly
      identifies its forensic value, subject to a retention policy
      that prevents premature loss of legal evidence and prevents
      indefinite retention of routine telemetry.

   Forensic-Grade Deliverability (FGD):
      An artifact set can be packaged into a form that satisfies the
      evidentiary chain-of-custody requirements of regulated industries:
      sealed, signed, self-contained, platform-independent, and capable
      of independent reconstruction years after creation.

   The Governance Evidence Gap is defined as:

      Gap_GE = (CRGA ∪ LAP ∪ FGD) − ICV

   An ATF-RGC-Compliant deployment without RFC-ATF-3 has Gap_GE > 0.
   Specifically:

      CRGA is undefined: no formal mechanism exists to declare that two
      runtimes agree on governance policy parameters.

      LAP is undefined: no formal evidence classification or retention
      policy binds what artifacts must be kept, summarized, or archived.

      FGD is undefined: no standardized forensic package format exists
      for ATF governance artifacts.

   RFC-ATF-3 closes Gap_GE by specifying GPIL (§5) for CRGA, ELR and
   EAP (§6, §7) for LAP, and OEP + FEA + FVP (§8, §9, §10) for FGD.


3.  Conventions and Terminology

   The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
   "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY",
   and "OPTIONAL" in this document are to be interpreted as described
   in BCP 14 [RFC2119] [RFC8174].

   This document uses all terms defined in RFC-ATF-1 §2 and RFC-ATF-2
   §3 without redefinition.  Additional terms introduced by this
   extension:

   Governance Policy Interoperability Layer (GPIL):
      The protocol layer (Layer 3 of the interoperability taxonomy,
      §5.1) governing agreement between ATF runtimes on configurable
      policy parameters within protocol-bounded ranges.

   Policy Divergence Surface:
      The parameter space where two fully RFC-ATF-2-compliant runtimes
      may reach different governance conclusions using identical
      artifacts.  Not a defect — a deliberate property of the sovereign
      runtime model.

   Cross-Runtime Governance Contract (CRGC):
      A bilateral, PQC-signed governance artifact that declares shared
      policy parameter values between two ATF runtimes, enabling Layer 3
      interoperability (GPIL).  Identified by CRGC-{16HEX}.

   ATF-GPI-Aligned:
      A compliance designation for ATF-RGC-Compliant runtimes that have
      established a valid CRGC with each counterpart runtime, achieving
      Layer 1 + Layer 2 + Layer 3 interoperability.

   Evidence Class:
      One of eight formally defined categories (§6.1) assigned to every
      governance artifact at write time, determining its retention tier,
      compression policy, and archival requirements.

   Retention Tier:
      One of three storage stages — HOT (active PostgreSQL), WARM
      (compressed aggregates), or COLD (immutable object storage) —
      through which artifacts progress according to their evidence class
      and age.

   Evidence Archive Pipeline (EAP):
      The mechanical implementation of the evidence lifecycle policy:
      the staged transition of artifacts from HOT to WARM to COLD with
      cryptographic integrity preservation at every stage.

   COLD Block:
      An immutable archive unit in COLD tier storage.  A COLD block
      contains one or more serialized governance artifacts, a Merkle
      integrity manifest, an ML-DSA-65 signature over the block's
      canonical hash, and a reference to the predecessor block's
      canonical hash — forming an append-only hash chain.

   OMNIX Evidence Package (OEP):
      A ZIP-format (.oep) cryptographically sealed, self-contained
      archive of governance evidence.  An OEP is the canonical forensic
      deliverable of an ATF-FEI-Compliant platform.  Identified by
      OEP-{YYYYMMDD}-{UUID8}.

   Two-Phase Package Signing:
      The signing protocol used for OEPs that avoids circular self-
      reference: the package signature is computed over the content
      manifest (manifest without the signature file entry), and the
      signature file entry is added to the manifest after signing.

   Platform Key Resolution:
      The ordered key selection procedure for OEP signing: prefer the
      platform environment key (OMNIX_SIGNING_SECRET_KEY_B64) over any
      caller-provided key.  Caller-provided keys are permitted only in
      development/test environments.

   Key Identity Object:
      The structured field returned by the /verify endpoint (§10.1)
      that identifies whether the public key used for verification
      matches the platform key — enabling machine-readable detection
      of verification oracle abuse.

   Evidence Custody Log:
      A non-deletable PostgreSQL table recording every tier transition
      for every archived artifact.  Classified as LEGAL evidence.

   ATF-FEI-Compliant:
      The compliance designation for implementations that satisfy all
      invariants of RFC-ATF-1, RFC-ATF-2, and RFC-ATF-3.  An ATF-FEI-
      Compliant implementation provides full Forensic Evidence
      Infrastructure capability: governance policy interoperability,
      evidence lifecycle management, and forensic-grade deliverability.


4.  Architecture: FEI Layer (Layer 5)

4.1.  Position in the ATF Stack

   RFC-ATF-3 adds a fifth operational layer to the four-layer ATF
   architecture:

   Layer 1 — Identity Plane (RFC-ATF-1 §4):
      Agent Identity Records.  PQC-signed agent registration.

   Layer 2 — Delegation Plane (RFC-ATF-1 §5):
      Delegation Receipts and Trust Lattice.  Monotonic Authority
      Reduction enforced at every delegation event.

   Layer 3 — Verification Plane (RFC-ATF-1 §8):
      Independent, offline receipt verification using only embedded
      public keys and stored artifacts.

   Layer 4 — Runtime Continuity Plane (RFC-ATF-2):
      Continuous authority health monitoring (CES), Authority
      Fragmentation Guard (AFG), Escalation Protocol, and
      Reauthorization Challenge (RC).

   Layer 5 — Forensic Evidence Infrastructure (RFC-ATF-3):
      Governance policy interoperability (GPIL), evidence lifecycle
      classification and retention (ELR), immutable archive pipeline
      (EAP), forensic package format (OEP), authenticated export (FEA),
      and forensic verification protocol (FVP).

   Layer 5 is non-destructive with respect to Layers 1–4.  It reads
   from the Delegation Plane and Runtime Continuity Plane.  A Layer 5
   failure MUST NOT affect the ability to issue, verify, or monitor
   governance artifacts.  The archive pipeline operates asynchronously
   and out of the request path.

4.2.  Extension Relationships

   RFC-ATF-3 extends the following prior specifications without
   modifying them:

   RFC-ATF-1: All six invariants (ATF-INV-001–006) remain unchanged.
   In particular, ATF-INV-006 (Independent Verifiability) is the
   foundational requirement that ELR-INV-001 (§6.7) and EAP-INV-005
   (§7.9) enforce across all lifecycle transitions.

   RFC-ATF-2: All eight invariants (RGC-INV-001–008) remain unchanged.
   In particular, RGC-INV-003 (HALT Propagation) is the trigger for
   EMERGENCY_COLD archival defined in §7.7.

   RFC-ATF-2 §21 (Interoperability Boundaries): RFC-ATF-3 §5 formalizes
   the GPIL specification introduced in RFC-ATF-2 §21.  The normative
   specification for GPIL is this document; RFC-ATF-2 §21 is the
   introductory treatment.


5.  Governance Policy Interoperability Layer (GPIL)

5.1.  Three-Layer Interoperability Taxonomy

   ATF-FEI-Compliant implementations recognize three distinct and
   formally separable interoperability levels:

   Layer 1 — Cryptographic Interoperability (CI):
      Scope: Signature verification of ATF artifacts (DR, TAR, RCR,
             CEE, RC, CRGC, COLD blocks, OEP packages).
      Requirement: Unconditional.  Any verifier holding the issuer's
                   ML-DSA-65 public key MUST be able to verify any
                   artifact.  Defined by ATF-INV-006 and this document.
      Variability: None.  Verification is binary: PASS or FAIL.

   Layer 2 — Protocol Interoperability (PI):
      Scope: Conformance to RFC-ATF-2 structural invariants
             (RGC-INV-001–008) and the CES computation protocol.
      Requirement: All ATF-RGC-Compliant implementations MUST satisfy
                   all eight RGC invariants without exception.
      Variability: None.  All invariants are hard constraints.

   Layer 3 — Governance Policy Interoperability (GPI):
      Scope: Agreement between runtimes on configurable governance
             policy parameters within protocol-defined bounds.
      Requirement: Optional.  Two runtimes MAY diverge on policy
                   parameters within their allowed ranges without
                   violating Protocol Interoperability.
      Variability: Full — within bounds defined in §5.2.

   The Policy Divergence Surface is entirely within Layer 3.  Layers 1
   and 2 are fully deterministic across all compliant runtimes.

   GPIL-INV-001 (defined formally in §5.5) establishes that this
   taxonomy is the normative framework for characterizing ATF
   interoperability claims.

5.2.  Policy Parameter Registry

   The following parameters are formally recognized as governance policy
   parameters: configurable by each sovereign runtime within the stated
   bounds.  A runtime operating outside these bounds is NOT compliant.

5.2.1.  Authority Fragmentation Guard Limit

   | Parameter              | Symbol                  | Default | Min  | Max  |
   |------------------------|-------------------------|---------|------|------|
   | AFG Fragmentation Limit| AFG_FRAGMENTATION_LIMIT | 0.90    | 0.01 | 0.95 |

   Hard maximum: 0.95.  Values above 0.95 MUST be rejected.
   Values above 1.0 MUST be rejected by the runtime at startup.

   Cross-runtime divergence example: Runtime A sets the limit to 0.80;
   Runtime B sets it to 0.95.  An aggregate reaching 85% of chain root
   budget is blocked by A but permitted by B.  Both are compliant.  The
   receipts they issue are cryptographically identical in structure.
   The governance conclusion differs.

5.2.2.  Reauthorization Challenge TTL

   | Parameter   | Symbol              | Default | Min | Max  |
   |-------------|---------------------|---------|-----|------|
   | RC TTL      | RGC_RC_TTL_SECONDS  | 300     | 30  | 3600 |

   Hard maximum: 3600 seconds.  The HALT decision on RC expiry is bound
   to the issuing runtime's TTL policy, not the verifier's.

5.2.3.  Context Drift Measurement Methodology

   RFC-ATF-2 defines context_drift_pct as an input to the CES formula
   but deliberately does not define how it is measured.  The measurement
   function MUST be monotonic in [0%, 100%].  Any monotonic function
   that meets this constraint is a valid implementation.

   Implication: Two runtimes measuring the same execution may report
   different context_drift_pct values for identical operational events,
   producing different CES scores.  Both are cryptographically valid.
   Neither runtime is non-compliant.  The governance status
   (NOMINAL vs. MONITORING) may legitimately differ.

5.2.4.  Anomaly Detection Criteria

   RFC-ATF-2 defines the I-component formula (max(0, 100 − anomalies
   × 10)) but not what constitutes a countable anomaly.  Runtimes MAY
   count events differently.  The integer count MUST be ≥ 0.

5.2.5.  Sampling Strategy Parameters

   | Parameter                   | Default | Allowed Range  |
   |-----------------------------|---------|----------------|
   | SHORT/NOMINAL interval      | 0s      | 0–60s          |
   | MEDIUM/NOMINAL interval     | 300s    | 60–3600s       |
   | LONG/NOMINAL interval       | 3600s   | 300–86400s     |
   | STREAMING/NOMINAL interval  | 30s     | 5–300s         |
   | Critical multiplier         | 6×      | 2×–20×         |

5.2.6.  Governance Risk Tier Assignment

   RFC-ATF-2 (extended by ADR-160) defines four risk tiers: LOW,
   STANDARD, HIGH, CRITICAL.  The assignment logic is implementation-
   defined, subject to: HIGH/CRITICAL tiers MUST use synchronous
   persistence (RGC-INV-003), and the LOW tier MAY skip PQC signing
   and database persistence for performance.

5.3.  Invariant Parameters (Non-Negotiable)

   The following parameters are NOT policy parameters.  They are
   protocol invariants fixed for all compliant implementations.  Any
   deviation constitutes non-compliance, regardless of other properties.

   | Parameter                | Fixed Value                              | Invariant      |
   |--------------------------|------------------------------------------|----------------|
   | CES formula              | T×0.30 + B×0.30 + D×0.20 + I×0.20      | RGC-INV-002    |
   | NOMINAL threshold        | CES ≥ 75.0                               | RFC-ATF-2 §6.3 |
   | MONITORING threshold     | 50.0 ≤ CES < 75.0                        | RFC-ATF-2 §6.3 |
   | WARNING threshold        | 25.0 ≤ CES < 50.0                        | RFC-ATF-2 §6.3 |
   | CRITICAL threshold       | 10.0 ≤ CES < 25.0                        | RFC-ATF-2 §6.3 |
   | HALT threshold           | CES < 10.0                               | RFC-ATF-2 §6.3 |
   | RC issuance range        | CRITICAL (10 ≤ CES < 25)                 | RFC-ATF-2 §10  |
   | B-component formula      | budget_remaining / budget_admission × 100| RGC-INV-002    |
   | I-component formula      | max(0, 100 − active_anomalies × 10)      | RGC-INV-002    |
   | T-component: expired DR  | 0.0                                      | RGC-INV-007    |
   | AFG hard maximum         | 0.95                                     | RFC-ATF-2 §8.2 |
   | content_hash algorithm   | SHA-256 over canonical JSON (sort_keys)  | RFC-ATF-2 §5.3 |
   | PQC algorithm            | ML-DSA-65 (FIPS 204)                     | RFC-ATF-2 §5.4 |
   | HALT → sibling revocation| Unconditional                            | RGC-INV-003    |
   | RC expiry → auto-HALT    | Unconditional                            | RGC-INV-008    |

5.4.  Cross-Runtime Governance Contracts (CRGC)

   When two or more ATF-RGC-Compliant runtimes require governance-
   aligned decisions (not merely cryptographic validity), they MUST
   establish a Cross-Runtime Governance Contract (CRGC).

   A CRGC is a bilateral, PQC-signed governance artifact — not merely
   a configuration file.  Both parties sign it with their respective
   ML-DSA-65 keys.  A CRGC does not modify protocol invariants (§5.3).
   It aligns sovereign policy parameters (§5.2) between the parties.

   CRGC wire format (canonical JSON):

   {
     "crgc_id":            "CRGC-{16HEX}",
     "parties":            ["runtime-A-identity", "runtime-B-identity"],
     "effective_from":     "ISO-8601",
     "expires_at":         "ISO-8601",
     "invariant_version":  "RFC-ATF-2-v1.0.0",
     "policy_parameters": {
       "afg_fragmentation_limit":          0.85,
       "rc_ttl_seconds":                   300,
       "context_drift_methodology_ref":    "task-scope-euclidean-v1",
       "anomaly_criteria_ref":             "OMNIX-ANOMALY-SPEC-v1",
       "sampling_profile":                 "STREAMING",
       "governance_risk_tier_policy":      "HIGH"
     },
     "content_hash":       "sha256:{hex}",
     "pqc_signatures":     [
       "{party-A-ML-DSA-65-signature}",
       "{party-B-ML-DSA-65-signature}"
     ]
   }

   content_hash is computed over all fields except {content_hash,
   pqc_signatures}, using the canonical JSON procedure (sort_keys=True,
   no whitespace separators, UTF-8 encoding, SHA-256 hex output).

   pqc_signatures is an ordered array aligned to parties[].  Both
   signatures MUST be present and valid for the CRGC to be effective.

   A CRGC is classified as CONTRACT evidence (§6.1) and is immutable
   from the moment of issuance.

5.5.  GPIL Compliance Designations

   ATF-RGC-Compliant (RFC-ATF-2):
      All eight RGC-INV invariants satisfied.  Policy parameters within
      protocol-defined bounds.  Provides Layer 1 + Layer 2
      interoperability.

   ATF-GPI-Aligned (RFC-ATF-3):
      ATF-RGC-Compliant AND the parties have established a valid,
      mutually PQC-signed CRGC.  Provides Layer 1 + Layer 2 + Layer 3
      interoperability — full governance agreement across runtimes, not
      merely cryptographic validity.

   The ATF-GPI-Aligned designation applies per-pair: a runtime may be
   ATF-GPI-Aligned with Runtime B while remaining only ATF-RGC-
   Compliant with respect to Runtime C (no CRGC with C established).

5.6.  GPIL Invariants

   GPIL-INV-001 — Interoperability Layer Separation:
      All interoperability claims for ATF implementations MUST be
      characterized using the three-layer taxonomy (§5.1).  A claim of
      "interoperability" without layer qualification is ambiguous and
      MUST NOT appear in compliance documentation.

   GPIL-INV-002 — Policy Parameter Bounds Enforcement:
      Every governance policy parameter (§5.2) MUST operate within its
      specified [min, max] range at all times.  A runtime detected
      operating outside these bounds is NOT ATF-RGC-Compliant regardless
      of any other properties.  In particular: AFG_FRAGMENTATION_LIMIT
      MUST NOT exceed 0.95; RGC_RC_TTL_SECONDS MUST NOT exceed 3600.

   GPIL-INV-003 — CRGC Signing Completeness:
      A CRGC is only effective if it carries valid ML-DSA-65 signatures
      from all parties declared in parties[].  A CRGC with a missing,
      invalid, or expired signature from any listed party is NOT a valid
      CRGC and does not establish ATF-GPI-Aligned status.


6.  Evidence Lifecycle Classification (ELR)

6.1.  Evidence Classes

   Every governance artifact produced by an ATF-FEI-Compliant platform
   MUST be assigned to exactly one evidence class at write time.  The
   class determines its retention tier, compression eligibility, and
   archival requirements.  Evidence class assignment is final at write
   time and subject to ELR-INV-003 (§6.7).

   | Class          | Code           | Examples                                   | Forensic Value            |
   |----------------|----------------|--------------------------------------------|---------------------------|
   | Legal Evidence | LEGAL          | decision_receipts, execution_receipts,     | Irreplaceable — non-       |
   |                |                | udcl_control_receipts                      | repudiable proof           |
   | PQC Chain      | PQC            | atf_delegations, atf_temporal_records,     | Irreplaceable — chain of   |
   |                |                | atf_domain_bridges, Dilithium-3 receipts   | verifiability              |
   | Cross-Runtime  | CONTRACT       | CRGCs (§5.4), governance_scope_            | Immutable bilateral        |
   |   Contract     |                | authorizations                             | agreement                  |
   | Exception Event| EXCEPTION      | RCRs at HALT/CRITICAL/FRAGMENTATION,       | Permanent forensic         |
   |                |                | atf_continuity_escalations, shadow events  | artifact                   |
   |                |                | with veto or anomaly, WARNING RCRs         |                            |
   | Runtime        | TELEMETRY      | RCRs with NOMINAL/MONITORING status,       | Summarizable after         |
   |   Telemetry    |                | avm_calibration_snapshots                  | retention window           |
   | Continuity     | SAMPLE         | atf_runtime_continuity rows tagged         | Aggregatable into          |
   |   Sample       |                | NOMINAL/HEALTHY                            | hourly snapshots           |
   | Shadow Nominal | SHADOW_NOMINAL | shadow_trade_events without veto,          | Compressible to            |
   |                |                | anomaly, or escalation                     | hash + metadata            |
   | Operational    | OPS            | b2b_clients, book_leads,                   | Standard business          |
   |                |                | paper_trading_balances                     | retention                  |

6.2.  Retention Tiers

6.2.1.  HOT Tier

   Duration:  0–90 days from creation (LEGAL, PQC, CONTRACT, EXCEPTION:
              indefinite — they never leave HOT unless transferred
              directly to COLD immutable archive).
   Storage:   PostgreSQL (or equivalent ACID-compliant RDBMS).
   Indexes:   Full — all query patterns supported.
   Access:    Real-time read/write.

6.2.2.  WARM Tier

   Duration:  90–365 days from creation.
   Eligible:  TELEMETRY, SAMPLE, SHADOW_NOMINAL, OPS.
   Ineligible: LEGAL, PQC, CONTRACT, EXCEPTION — these remain in HOT
               indefinitely or move directly to COLD.
   Storage:   PostgreSQL with compressed aggregates and reduced indexes.
   Indexes:   Audit and hash-lookup only.
   Access:    Read-only after promotion from HOT.

   Every HOT→WARM transition MUST create a WARM manifest entry (§7.3)
   before any transformation occurs.  Transitions without a manifest
   entry are invalid (EAP-INV-006).

6.2.3.  COLD Tier

   Duration:  365+ days; permanent for immutable classes.
   Storage:   S3-compatible object storage with object lock enabled
              and versioning disabled (append-only).
   Format:    Parquet segments within JSON COLD block files, each block
              carrying a SHA-256 Merkle manifest and ML-DSA-65 signature.
   Indexes:   None — hash-addressed lookup only.
   Access:    Archival verification only.

   COLD artifacts MUST preserve content_hash and pqc_signatures in
   their original form to satisfy ATF-INV-006 (Independent
   Verifiability) and ELR-INV-001 (§6.7).

6.3.  Retention Policy Matrix

   | Evidence Class | HOT         | WARM           | COLD                      | Deletion              |
   |----------------|-------------|----------------|---------------------------|-----------------------|
   | LEGAL          | Permanent   | Never          | Optional immutable archive| Never                 |
   | PQC            | Permanent   | Never          | Optional immutable archive| Never                 |
   | CONTRACT       | Permanent   | Never          | Optional immutable archive| Never                 |
   | EXCEPTION      | Permanent   | Never          | Optional immutable archive| Never                 |
   | TELEMETRY      | 90 days     | 90–365 days    | Aggregated snapshot       | After COLD aggregation|
   | SAMPLE         | 30 days     | Aggregated     | Compressed timeline       | After aggregation     |
   | SHADOW_NOMINAL | 30 days     | Hash+meta only | Compressed                | After COLD compression|
   | OPS            | Active life | 90–365 days    | Optional                  | Per business policy   |

6.4.  Shadow Event Reduction Policy

   High-volume SHADOW_NOMINAL artifacts (e.g., shadow_trade_events)
   MUST apply write-time payload reduction.  Classification occurs at
   write time, not retroactively.

   | Event Classification    | Fields Stored                                                    |
   |-------------------------|------------------------------------------------------------------|
   | Veto triggered          | Full payload (reclassified EXCEPTION — permanent)                |
   | Anomaly detected        | Full payload (reclassified EXCEPTION — permanent)                |
   | Escalation raised       | Full payload (reclassified EXCEPTION — permanent)                |
   | Critical risk tier      | Full payload (reclassified EXCEPTION — permanent)                |
   | Nominal / healthy       | event_id, timestamp_ns, event_type, agent_id,                   |
   |                         | content_hash, risk_score only                                    |

   Implementations applying this reduction MUST achieve approximately
   80% volume reduction for deployments where nominal events dominate.
   The reduction is not retroactive; existing nominal rows require
   auditor sign-off before retroactive compression.

6.5.  RCR Summarization Policy

   Runtime Continuity Records from the atf_runtime_continuity table
   are classified and retained as follows:

   HALT, CRITICAL, FRAGMENTATION, ESCALATION RCRs:
      Classification: EXCEPTION.  Retention: Permanent.

   WARNING RCRs:
      Classification: EXCEPTION.  Retention: Permanent.
      (Threshold crossing events are forensically relevant.)

   MONITORING RCRs:
      Classification: TELEMETRY.  Retention: Summarizable after 90 days.

   NOMINAL / HEALTHY RCRs:
      Classification: SAMPLE.  Retention: Aggregatable into hourly
      snapshots (rcr_hourly_aggregate) after 30 days.

   Hourly aggregate schema for SAMPLE compression:

   rcr_hourly_aggregate(
       hour_bucket          TIMESTAMPTZ,
       chain_root_id        TEXT,
       domain               TEXT,
       sample_count         INTEGER,
       avg_ces_score        FLOAT,
       min_ces_score        FLOAT,
       status_distribution  JSONB,   -- {"NOMINAL": 847, "MONITORING": 12}
       first_rcr_id         TEXT,
       last_rcr_id          TEXT,
       content_hash         TEXT     -- hash of aggregate, not individual RCRs
   )

   Individual NOMINAL RCRs MAY be dropped after aggregation.  The
   aggregate is a telemetry summary, not a forensic substitute for
   original EXCEPTION-class records.

6.6.  Database Maintenance Policy

   Independently of lifecycle tiers, ATF-FEI-Compliant platforms MUST
   adopt the following maintenance operations:

   (a) Dead index removal: indexes with zero scans over 30 days are
       candidates for removal; duplicate indexes (same columns, same
       table) are removed unconditionally.

   (b) VACUUM schedule: VACUUM ANALYZE runs weekly on all tables and
       immediately after any bulk operation producing more than 10,000
       dead tuples.

   (c) Autovacuum tuning: high-turnover tables (e.g.,
       avm_calibration_snapshots) SHOULD use
       autovacuum_vacuum_scale_factor = 0.01 and
       autovacuum_analyze_scale_factor = 0.005.

6.7.  ELR Invariants

   ELR-INV-001 — Verifiability Preservation:
      Any artifact moved to WARM or COLD tier MUST retain its
      content_hash and pqc_signatures (where present) in a form that
      allows offline verification per ATF-INV-006.  Compression and
      format changes are permitted; hash mutation is not.

   ELR-INV-002 — Exception Permanence:
      No artifact classified as EXCEPTION, LEGAL, PQC, or CONTRACT may
      be deleted, truncated, or compressed in a way that reduces its
      forensic completeness, regardless of age.

   ELR-INV-003 — Classification Immutability:
      Once an artifact is assigned an evidence class at write time,
      its class cannot be downgraded.  Reclassification to a higher-
      forensic-value class is permitted (e.g., SHADOW_NOMINAL →
      EXCEPTION upon veto detection) and takes effect immediately and
      permanently.

   ELR-INV-004 — HOT Retention Minimum:
      All evidence classes MUST remain in HOT tier for a minimum of 30
      days from creation, regardless of volume pressure.  No automated
      process may promote an artifact to WARM before this minimum.


7.  Immutable Evidence Archive Pipeline (EAP)

7.1.  Pipeline Stage Overview

   The Evidence Archive Pipeline (EAP) defines the mechanical
   implementation of the evidence lifecycle policy (§6): the concrete
   procedure for transitioning artifacts from HOT to WARM to COLD with
   cryptographic integrity preservation at every stage.

   The governing principle is:

      Storage efficiency is a secondary concern.
      Offline reconstructability is a hard requirement.

7.2.  HOT Stage

   Duration:  0–90 days (LEGAL/PQC/CONTRACT/EXCEPTION: indefinite).
   Integrity:  PostgreSQL ACID + WAL.
   Write path: Direct from governance engine; RPOL write queue (ADR-160)
               for RCRs.
   Transformation: None.  All artifacts stored in canonical form.

7.3.  WARM Stage and Transition Manifest

   Before any compression or transformation, the original content_hash
   MUST be written to a WARM manifest entry:

   CREATE TABLE IF NOT EXISTS warm_archive_manifest (
       manifest_id          TEXT PRIMARY KEY,
       original_artifact_id TEXT NOT NULL,
       evidence_class       TEXT NOT NULL,
       original_hash        TEXT NOT NULL,    -- content_hash before compression
       compressed_hash      TEXT NOT NULL,    -- hash of compressed form
       compression_method   TEXT NOT NULL,    -- 'aggregate_hourly' | 'strip_nominal' | 'none'
       promoted_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
       promoted_by          TEXT NOT NULL DEFAULT 'lifecycle_pipeline',
       integrity_verified   BOOLEAN NOT NULL DEFAULT FALSE
   );

   Transformation rules by evidence class:

   TELEMETRY / SAMPLE → compressed into rcr_hourly_aggregate (§6.5).
   SHADOW_NOMINAL     → stripped to {event_id, timestamp_ns,
                        event_type, agent_id, content_hash, risk_score}.
   Other classes      → MUST NOT enter WARM (ELR-INV-002).

7.4.  COLD Stage: Block Format

   COLD stage stores artifacts in structured JSON block files with
   deterministic naming: OMNIX-BLOCK-{YYYYMMDD}-{seq:06d}.json

   Each block carries the following structure (canonical JSON):

   {
     "block_id":               "OMNIX-BLOCK-{YYYYMMDD}-{sequence:06d}",
     "creation_timestamp_ns":  {Unix nanosecond timestamp},
     "artifact_count":         {integer},
     "evidence_classes":       [{array of class codes present in block}],
     "canonical_hash":         "sha256:{hex}",
     "predecessor_block_hash": "sha256:{hex}",
     "integrity_manifest": {
       "artifact_hashes": ["sha256:{hex}", ...],
       "merkle_root":     "sha256:{hex}",
       "hash_algorithm":  "sha256-v1"
     },
     "pqc_signature":  "{ML-DSA-65 signature over canonical_hash bytes}",
     "pqc_algorithm":  "ML-DSA-65 (FIPS 204)",
     "omnix_version":  "1.0.0"
   }

   canonical_hash is computed as SHA-256 over the canonical JSON of
   the block WITHOUT the pqc_signature field (which does not yet exist
   at hash computation time).

   merkle_root is computed by SHA-256 hashing the sorted, newline-
   joined concatenation of all artifact_hashes.

   pqc_signature is computed by signing canonical_hash.encode('utf-8')
   with the platform ML-DSA-65 private key.

7.5.  Block Chaining

   The predecessor_block_hash field of each COLD block references the
   canonical_hash of the immediately preceding block in temporal order.
   The genesis block uses the sentinel value:

      predecessor_block_hash = "0" × 64

   This creates an append-only hash chain across all COLD archive
   blocks.  Tampering with any block breaks every subsequent link in
   the chain.

   Block files MUST be named deterministically
   (OMNIX-BLOCK-{YYYYMMDD}-{seq:06d}.json) to enable chain
   reconstruction from filenames alone.

7.6.  Offline Verifier Extension

   The omnix_atf_verify.py CLI (originally defined in RFC-ATF-1, §8)
   MUST be extended with an --archive-block mode for COLD block
   verification.  The extended signature:

   python omnix_atf_verify.py \
     --archive-block OMNIX-BLOCK-20260514-000001.json \
     --public-key    omnix_public_key.b64 \
     --mode          block \
     [--verify-chain --predecessor-block OMNIX-BLOCK-20260514-000000.json]

   Verification steps (all offline, no platform access permitted):

   Step 1: Load block manifest.
   Step 2: Recompute canonical_hash from integrity_manifest.merkle_root
           using the SHA-256 sorted-join procedure.
   Step 3: Verify ML-DSA-65 signature over canonical_hash bytes using
           the provided public key.
   Step 4: (If --verify-chain): Verify predecessor_block_hash matches
           the predecessor block's canonical_hash.
   Step 5: For each artifact: recompute content_hash from artifact
           fields, verify against integrity_manifest.artifact_hashes.
   Step 6: Emit JSON verification report with verdict.

   Verdicts: PASS | INTEGRITY_VIOLATION | CHAIN_BREAK | SIGNATURE_INVALID

   The verifier MUST use only pypqc (pqc.sign.dilithium3) for ML-DSA-65
   operations.  Fallback to alternative libraries is prohibited
   (FVP invariant; see §10.4).

7.7.  Pipeline Trigger Model

   The archive pipeline runs as a scheduled background process, out of
   the request path.

   | Trigger                   | Action                                            |
   |---------------------------|---------------------------------------------------|
   | Daily at 02:00 UTC        | HOT→WARM for TELEMETRY/SAMPLE/SHADOW_NOMINAL      |
   |                           | artifacts older than 90 days                      |
   | Weekly Sunday at 03:00 UTC| WARM→COLD block sealing for artifacts > 365 days  |
   | On demand (admin)         | Force-seal current WARM batch to COLD             |
   | On governance HALT        | EMERGENCY_COLD: immediate COLD seal of all        |
   |                           | EXCEPTION-class artifacts from halted chain root  |

   The EMERGENCY_COLD trigger is the most critical operational mode.
   When RGC-INV-003 fires a HALT event, all artifacts associated with
   the halted chain root are immediately sealed to COLD regardless of
   age, closing the evidentiary window at the moment of the halt.

   No post-HALT modification of evidence from that chain root is
   possible after EMERGENCY_COLD sealing.

7.8.  Evidence Custody Log

   Every pipeline transition MUST create a non-deletable entry in the
   evidence custody log:

   CREATE TABLE IF NOT EXISTS evidence_custody_log (
       custody_id          TEXT PRIMARY KEY,
       artifact_id         TEXT NOT NULL,
       evidence_class      TEXT NOT NULL,
       transition          TEXT NOT NULL,   -- 'HOT->WARM' | 'WARM->COLD' | 'EMERGENCY_COLD'
       from_hash           TEXT NOT NULL,
       to_hash             TEXT NOT NULL,
       block_id            TEXT,            -- populated for COLD transitions
       triggered_by        TEXT NOT NULL,   -- 'scheduler' | 'halt_event' | 'admin'
       transition_ns       BIGINT NOT NULL,
       integrity_verified  BOOLEAN NOT NULL DEFAULT FALSE,
       verified_at         TIMESTAMPTZ,
       notes               TEXT
   );

   This table is classified as LEGAL evidence.  It MUST NOT be deleted,
   truncated, or modified by any process.  The evidence_custody_log
   together with the COLD block chain forms the complete chain of
   custody for every governance artifact the platform produces.

7.9.  EAP Invariants

   EAP-INV-001 — Verification Preservation:
      Any artifact transitioned to WARM or COLD MUST have its original
      content_hash recorded in the transition manifest before any
      transformation.  The hash MUST be recomputable from the original
      artifact fields as defined in the issuing ADR.

   EAP-INV-002 — PQC Signature Preservation:
      Any artifact bearing an ML-DSA-65 signature (pqc_signatures array)
      MUST have that signature array preserved in COLD storage in its
      original unmodified form.  Compression of other fields is
      permitted; the signature array is untouchable.

   EAP-INV-003 — Block Chain Integrity:
      The predecessor_block_hash chain across all COLD blocks MUST be
      unbroken.  Any gap in the chain (missing predecessor) constitutes
      an integrity violation.  The pipeline validator MUST check chain
      continuity before sealing any new block.

   EAP-INV-004 — Immutable Class Permanence:
      Evidence artifacts of class LEGAL, PQC, CONTRACT, and EXCEPTION
      MUST be sealed in COLD storage in their complete canonical form.
      No field stripping, no payload reduction, no compression of any
      kind is permitted.  The full artifact as emitted by the governance
      engine MUST be preserved.

   EAP-INV-005 — Offline Reconstructability:
      An auditor MUST be able, using only: a COLD archive block file,
      the issuer's ML-DSA-65 public key, and the omnix_atf_verify.py
      CLI (version shipped with the block), to verify: block integrity,
      PQC signatures, predecessor chain, and artifact content hashes.
      No OMNIX runtime, no database access, and no API calls are
      permitted in this verification path.

   EAP-INV-006 — Manifest Completeness:
      Every HOT→WARM and WARM→COLD transition MUST create a manifest
      entry before the transition completes.  Transitions without a
      manifest entry are invalid and MUST be rolled back.

   EAP-INV-007 — Globally Unique Block IDs:
      Block IDs MUST be globally unique across the platform lifetime.
      In production deployments with REDIS_URL configured, uniqueness
      MUST be guaranteed by atomic Redis INCR using the key schema
      omnix:block_seq:{YYYYMMDD} with a 30-day TTL.  In development or
      test environments without Redis, uniqueness is best-effort within
      a single process.  The in-process fallback MUST emit a WARNING
      log entry documenting that global uniqueness is not guaranteed.


8.  OMNIX Evidence Package (OEP)

8.1.  Physical Format

   An OEP is a ZIP-format archive using the .oep extension.  The file
   name pattern is:

      OMNIX-PACKAGE-{YYYYMMDD}-{UUID8}.oep

   The archive MUST use ZIP64 for packages exceeding 4 GB.  Compression
   level: DEFLATE for all files except REPORT/forensic_report.html,
   which is stored uncompressed for immediate browser rendering.

   Anti-zip-slip protection: the OEP generator MUST validate that no
   file path resolves outside the archive root.  The OEP extractor MUST
   sanitize all extracted paths before writing to disk.

8.2.  Directory Structure

   An OEP MUST contain exactly the following directory structure:

   OMNIX-PACKAGE-{DATE}-{ID}.oep
   ├── META/
   │   ├── manifest.json              ← Package manifest (signed)
   │   └── README.txt                 ← Human-readable instructions
   ├── BLOCKS/
   │   ├── OMNIX-BLOCK-*.json         ← COLD blocks in chain order
   │   └── chain_index.json           ← [{block_id, canonical_hash, seq}]
   ├── KEYS/
   │   └── public_key.b64             ← Issuer ML-DSA-65 public key (base64)
   ├── VERIFY/
   │   ├── omnix_atf_verify.py        ← Offline CLI verifier (v1.1.0+)
   │   └── verify_all.sh              ← Shell script: full chain verification
   ├── CUSTODY/
   │   └── evidence_custody_log.json  ← Custody log entries for all blocks
   ├── REPORT/
   │   └── forensic_report.html       ← Forensic reconstruction report (offline HTML)
   └── SIGNATURE/
       └── package_signature.json     ← ML-DSA-65 signature over canonical manifest hash

8.3.  Package Manifest Schema

   META/manifest.json — field-sorted canonical JSON:

   {
     "manifest_version": "oep-1.0",
     "package_id":       "OEP-{YYYYMMDD}-{UUID8}",
     "created_at":       "{ISO-8601 UTC}",
     "generator":        "OMNIX Evidence Archive Pipeline",
     "generator_version": "1.0.0",
     "algorithms": {
       "hash":      "sha256-v1",
       "signature": "ML-DSA-65 (FIPS 204)",
       "merkle":    "sha256-v1 sorted-join"
     },
     "chain": {
       "head_block_id":    "{block_id}",
       "head_block_hash":  "sha256:{hex}",
       "genesis_sentinel": "0000...0000",   -- 64 zeros
       "block_count":      {integer},
       "span_ns": {
         "earliest": {ns timestamp},
         "latest":   {ns timestamp}
       }
     },
     "evidence": {
       "total_artifacts":  {integer},
       "evidence_classes": [{array of class codes}],
       "immutable_only":   {boolean}
     },
     "custody": {
       "entry_count": {integer},
       "log_sha256":  "{sha256 of evidence_custody_log.json bytes}"
     },
     "public_key": {
       "algorithm":    "ML-DSA-65 (FIPS 204)",
       "fingerprint":  "sha256:{first-32-hex-chars of sha256(key_bytes)}",
       "file":         "KEYS/public_key.b64"
     },
     "files": [
       { "path": "META/manifest.json",               "sha256": "{hex}", "size_bytes": {n}, "media_type": "application/json" },
       { "path": "META/README.txt",                  "sha256": "{hex}", "size_bytes": {n}, "media_type": "text/plain" },
       { "path": "BLOCKS/chain_index.json",          "sha256": "{hex}", "size_bytes": {n}, "media_type": "application/json" },
       { "path": "KEYS/public_key.b64",              "sha256": "{hex}", "size_bytes": {n}, "media_type": "text/plain" },
       { "path": "VERIFY/omnix_atf_verify.py",      "sha256": "{hex}", "size_bytes": {n}, "media_type": "text/x-python" },
       { "path": "VERIFY/verify_all.sh",             "sha256": "{hex}", "size_bytes": {n}, "media_type": "text/x-shellscript" },
       { "path": "CUSTODY/evidence_custody_log.json","sha256": "{hex}", "size_bytes": {n}, "media_type": "application/json" },
       { "path": "REPORT/forensic_report.html",      "sha256": "{hex}", "size_bytes": {n}, "media_type": "text/html" },
       { "path": "SIGNATURE/package_signature.json", "sha256": "{hex}", "size_bytes": {n}, "media_type": "application/json" }
     ],
     "signature_metadata": {
       "signed_object": "canonical_manifest_hash",
       "algorithm":     "ML-DSA-65 (FIPS 204)",
       "signed_at":     "{ISO-8601 UTC}"
     }
   }

8.4.  Two-Phase Package Signing Protocol

   The OEP signing protocol avoids circular self-reference by a two-
   phase procedure.

   Phase 1 — Compute canonical manifest hash:

   The signed object is the content manifest: manifest.json with the
   SIGNATURE/package_signature.json entry removed from files[].
   This entry cannot exist at signing time.

      content_manifest = manifest WITHOUT files entry for
                         "SIGNATURE/package_signature.json"
      canonical_bytes  = json.dumps(
                           content_manifest,
                           sort_keys=True,
                           separators=(',', ':'),
                           ensure_ascii=False
                         ).encode('utf-8')
      canonical_manifest_hash = "sha256:" + sha256(canonical_bytes).hexdigest()

   Phase 2 — Finalize and seal:

   1. Sign canonical_manifest_hash.encode('utf-8') with the ML-DSA-65
      private key → pqc_signature (base64).
   2. Build SIGNATURE/package_signature.json with canonical_manifest_hash
      and pqc_signature.
   3. Compute SHA-256 of package_signature.json bytes → add entry to
      manifest.files[].
   4. Write final manifest.json (now including the signature file entry)
      and package_signature.json to the ZIP archive.

   SIGNATURE/package_signature.json wire format:

   {
     "package_id":               "OEP-{YYYYMMDD}-{UUID8}",
     "canonical_manifest_hash":  "sha256:{hex}",
     "pqc_signature":            "{base64-ML-DSA-65 signature}",
     "pqc_algorithm":            "ML-DSA-65 (FIPS 204)",
     "public_key_fingerprint":   "sha256:{fingerprint}",
     "signed_at":                "{ISO-8601 UTC}"
   }

8.5.  Independent Verification Procedure

   An auditor verifies an OEP using only the package file and a
   standard Python 3.10+ installation with pypqc:

   import json, hashlib, base64
   from pqc.sign import dilithium3

   manifest = json.load(open('META/manifest.json'))
   sig_data = json.load(open('SIGNATURE/package_signature.json'))

   # Reconstruct content_manifest (strip SIGNATURE entry)
   content_manifest = dict(manifest)
   content_manifest['files'] = [
       f for f in manifest['files']
       if f['path'] != 'SIGNATURE/package_signature.json'
   ]

   # Verify canonical hash
   canonical_bytes = json.dumps(
       content_manifest, sort_keys=True,
       separators=(',', ':'), ensure_ascii=False
   ).encode('utf-8')
   computed = 'sha256:' + hashlib.sha256(canonical_bytes).hexdigest()
   assert computed == sig_data['canonical_manifest_hash'], 'MANIFEST TAMPERED'

   # Verify ML-DSA-65 signature
   pk  = base64.b64decode(open('KEYS/public_key.b64').read().strip())
   sig = base64.b64decode(sig_data['pqc_signature'])
   dilithium3.verify(sig, computed.encode('utf-8'), pk)  # raises ValueError if invalid
   print("VALID")

   No network access, no OMNIX credentials, and no external service
   calls are required or permitted in this procedure.

8.6.  Forensic Reconstruction Report

   REPORT/forensic_report.html is a self-contained HTML file with all
   CSS inline and all visualizations rendered as inline SVG.  No
   external dependencies of any kind are permitted — no CDN, no Google
   Fonts, no external scripts.

   The report MUST contain the following sections:
   (a) Executive Summary: package ID, creation date, block count, verdict.
   (b) Block Chain: ordered table of block IDs, timestamps, artifact
       counts, canonical hashes, and PQC verification status.
   (c) Evidence Class Breakdown: count, first/last timestamp per class.
   (d) Authority Timeline: custody log events ordered by transition_ns.
   (e) Integrity Verification Trace: per-block Merkle ✓/✗, canonical
       ✓/✗, chain ✓/✗, PQC ✓/✗.
   (f) Appendix: Verification Instructions for running
       omnix_atf_verify.py against each block.

   When the custody log is truncated for display (e.g., to the first
   200 entries), the report MUST display a prominent amber warning:

      "⚠ Report shows first {n} of {total} custody entries.
       Full custody log available in CUSTODY/evidence_custody_log.json
       within this package."

   A report that silently omits evidence is forensically indefensible.

8.7.  OEP Invariants

   OEP-INV-001 — Offline Self-Containment:
      An OEP MUST be verifiable with only the package file and a
      standard Python 3.10+ installation with pypqc.  No network access,
      no OMNIX credentials, and no external dependencies are permitted
      during verification.

   OEP-INV-002 — File Integrity Lattice:
      Every file in the OEP MUST appear in files[] in manifest.json
      with its correct SHA-256.  A package containing any file not
      listed in the manifest is invalid.  A package where any listed
      file's hash does not match the computed hash is invalid.

   OEP-INV-003 — Mandatory Package Signature:
      SIGNATURE/package_signature.json MUST be present and MUST contain
      a valid ML-DSA-65 signature over the canonical manifest hash.
      An OEP without a valid package signature is not a valid OEP.

   OEP-INV-004 — Chain Completeness:
      If a block in BLOCKS/ references a predecessor_block_hash that is
      not the genesis sentinel, the predecessor block MUST also appear
      in BLOCKS/.  An OEP with a chain gap is invalid.

   OEP-INV-005 — Embedded Public Key:
      KEYS/public_key.b64 MUST contain the public key that verifies
      both the COLD blocks and the package signature.  Referencing a
      key by URL is not permitted — the key MUST be embedded.

   OEP-INV-006 — Schema Version Lock:
      manifest_version MUST be "oep-1.0" for packages generated under
      this specification.  Future schema changes require a new version
      string and a new protocol revision.  Parsers MUST reject packages
      with unrecognized manifest_version values.


9.  Forensic Export Authentication (FEA)

9.1.  Authentication Gate

   The OEP generation endpoint (POST /api/forensic/export) MUST require
   a valid X-API-Key header authenticated against the b2b_clients table
   with role = 'admin'.  Unauthenticated requests or requests with
   role = 'standard' MUST receive HTTP 401 Unauthorized.

   Read-only forensic endpoints (GET /api/forensic/status,
   POST /api/forensic/verify) MUST remain public — they perform no key
   operations and return no private data.

9.2.  Platform Key Resolution

   The OEP generation endpoint MUST resolve signing keys in the
   following priority order:

   | Priority | Condition                                         | Result                      |
   |----------|---------------------------------------------------|-----------------------------|
   | 1        | FORENSIC_EXPORT_ALLOW_CALLER_KEYS=true AND caller | Use caller key              |
   |          | provides secret_key_b64 in request body           | (key_source = "caller")     |
   | 2        | OMNIX_SIGNING_SECRET_KEY_B64 present in           | Use platform key            |
   |          | server environment                                | (key_source = "platform")   |
   | 3        | Neither condition satisfied                       | Return 503 Fail-Closed      |
   |          |                                                   | (OEP-INV-003 cannot be met) |

   FORENSIC_EXPORT_ALLOW_CALLER_KEYS defaults to false and MUST NOT be
   set to true in production.  It exists exclusively for local
   development and integration testing.  This environment variable is a
   deliberate deployment friction mechanism to prevent production
   misconfiguration.

   Similarly, public_key_b64 falls back to OMNIX_SIGNING_PUBLIC_KEY_B64
   from the server environment when absent from the request.

9.3.  Audit Logging

   Every OEP export MUST create a non-repudiable audit log entry
   containing: client_id, client_name, ip_address, package_id,
   key_source ('platform' | 'caller'), block_count, and timestamp.

   This log establishes a chain of custody for who requested which OEP
   and under what authentication context.

9.4.  FEA Invariants

   FEA-INV-001 — Key Isolation:
      The ML-DSA-65 private key used for OEP signing MUST NOT be
      transmitted in HTTP request bodies in production.  Platform key
      resolution (§9.2) enforces this invariant by reading the key from
      the server environment, never from the caller.

   FEA-INV-002 — Export Audit Non-Repudiation:
      Every OEP export MUST be logged with client_id, ip_address,
      key_source, and package_id before the package is returned to the
      caller.  An export without an audit log entry is a protocol
      violation.

   FEA-INV-003 — Authentication Required:
      POST /api/forensic/export MUST return 401 for any request with a
      missing, invalid, or expired API key.

   FEA-INV-004 — Fail-Closed on Key Absence:
      POST /api/forensic/export MUST return 503 when no signing key is
      available (neither platform environment key nor permitted caller
      key).  The endpoint MUST NOT generate an unsigned OEP.

   FEA-INV-005 — Caller Key Production Prohibition:
      FORENSIC_EXPORT_ALLOW_CALLER_KEYS=true is forbidden in
      production.  Any deployment with this variable set to true MUST be
      treated as a development environment and MUST NOT issue OEPs
      intended for regulatory submission.


10.  Forensic Verification Protocol (FVP)

10.1.  Key Identity Fingerprinting

   The POST /api/forensic/verify endpoint intentionally accepts
   arbitrary public keys to allow offline verification of any ML-DSA-65-
   signed data — this is required by EAP-INV-005.  However, without key
   identity disclosure, an adversary can submit a block signed with an
   arbitrary key, receive a PASS verdict from the OMNIX server, and
   present that verdict as platform endorsement.

   To prevent this, every /verify response MUST include a key_identity
   object:

   {
     "key_identity": {
       "provided_fingerprint":  "sha256:{hex}",
       "platform_fingerprint":  "sha256:{hex}",   -- null if platform key not configured
       "matches_platform":      true | false | null,
       "warning":               null | "{warning text}"
     }
   }

   provided_fingerprint: SHA-256 of the public key bytes provided by
   the caller (base64-decoded).

   platform_fingerprint: SHA-256 of the OMNIX_SIGNING_PUBLIC_KEY_B64
   environment variable bytes.  null when the variable is not set.

   matches_platform: true when both fingerprints are present and equal.
   null when either is absent.

   warning: non-null when matches_platform is false or when the
   platform key is not server-side-configured.  When non-null for a
   mismatched key, the warning text MUST include:

      "PROVIDED KEY DOES NOT MATCH OMNIX PLATFORM KEY — this block
       was not signed by OMNIX QUANTUM LTD.  A PASS verdict here is
       NOT a platform endorsement."

   Logging requirement: Every /verify request where matches_platform
   is false MUST produce a WARNING log entry containing the provided
   fingerprint, the platform fingerprint, and the client IP.

10.2.  Distributed Block Sequencing

   In production deployments with REDIS_URL configured, the
   _next_block_id() function MUST use Redis INCR as its sequence source.

   Redis key schema: omnix:block_seq:{YYYYMMDD}
   TTL: 30 days.  Set with EXPIRE ... NX on first increment to avoid
   resetting an existing TTL.
   Atomicity: Redis INCR is atomic by definition.  No locking or
   transactions are required.

   Fallback: When REDIS_URL is not set or Redis is unreachable at call
   time, the function MUST fall back to an in-process counter and MUST
   emit a WARNING log documenting that global uniqueness is not
   guaranteed.  This fallback MUST NOT be triggered in environments
   where TESTING=true.

   See EAP-INV-007 (§7.9) for the invariant governing block ID
   uniqueness.

10.3.  Distributed Rate Limiting

   Rate limiting for forensic API endpoints MUST be backed by Redis
   when REDIS_URL is configured.  In-memory rate limiting is permitted
   only in local development environments.

   Rationale: With N deployment dynos, in-memory storage produces N
   independent rate counters.  The effective per-IP rate limit becomes
   N × configured_limit.  Since deployments may auto-scale under load,
   in-memory rate limiting produces a perverse incentive: a volumetric
   attack that triggers auto-scaling simultaneously raises the effective
   rate limit.  Redis INCR-based counters are shared across all dynos,
   making the configured limit a true per-IP ceiling regardless of
   scale.

10.4.  Verifier Library Determinism

   omnix_atf_verify.py MUST use only pypqc (pqc.sign.dilithium3) for
   ML-DSA-65 verification.  Alternative library fallbacks are
   permanently prohibited.

   When pypqc is not installed, the verifier MUST return:

      (False, "UNAVAILABLE",
       "pypqc not installed.  Install with: pip install pypqc\n"
       "pypqc is the only supported library for ML-DSA-65 verification
       in this tool.")

   Rationale: ML-DSA-65 is standardized in FIPS 204, but library
   implementations may differ in byte packing, encoding, or API
   contracts.  A verifier that silently switches libraries can produce
   verdicts that are not reproducible across installations — violating
   the determinism requirement of EAP-INV-005.

   Additionally: omnix_atf_verify.py MUST NOT import from the OMNIX
   platform codebase (omnix_core or any package not available from the
   public PyPI index).  Any platform import in the standalone verifier
   is a violation of EAP-INV-005 (offline reconstructability).

10.5.  FVP Invariants

   FVP-INV-007 — Key Identity Disclosure:
      Every /api/forensic/verify response MUST include a key_identity
      object.  When the platform key is configured server-side,
      platform_fingerprint MUST be populated.  Suppressing key_identity
      or returning null for platform_fingerprint when the platform key
      is available is not permitted.


11.  Combined Invariant Summary

   The following table summarizes all twenty-six invariants introduced
   by RFC-ATF-3, in addition to the fourteen invariants established by
   RFC-ATF-1 (ATF-INV-001–006) and RFC-ATF-2 (RGC-INV-001–008).

   | ID             | Statement (summary)                               | Section |
   |----------------|---------------------------------------------------|---------|
   | GPIL-INV-001   | Interoperability claims MUST use 3-layer taxonomy | §5.6    |
   | GPIL-INV-002   | Policy parameters MUST stay within defined bounds | §5.6    |
   | GPIL-INV-003   | CRGC requires valid signatures from all parties   | §5.6    |
   | ELR-INV-001    | WARM/COLD transitions preserve content_hash       | §6.7    |
   | ELR-INV-002    | EXCEPTION/LEGAL/PQC/CONTRACT never deleted        | §6.7    |
   | ELR-INV-003    | Evidence class cannot be downgraded at write time | §6.7    |
   | ELR-INV-004    | All classes remain HOT minimum 30 days            | §6.7    |
   | EAP-INV-001    | content_hash recorded before any transformation  | §7.9    |
   | EAP-INV-002    | pqc_signatures preserved verbatim in COLD         | §7.9    |
   | EAP-INV-003    | predecessor_block_hash chain must be unbroken     | §7.9    |
   | EAP-INV-004    | Immutable classes sealed complete in COLD         | §7.9    |
   | EAP-INV-005    | Offline reconstructability — no platform required | §7.9    |
   | EAP-INV-006    | Every transition requires a manifest entry        | §7.9    |
   | EAP-INV-007    | Block IDs globally unique via Redis INCR in prod  | §7.9    |
   | OEP-INV-001    | OEP verifiable offline with pypqc only            | §8.7    |
   | OEP-INV-002    | All OEP files listed in manifest with SHA-256     | §8.7    |
   | OEP-INV-003    | Package signature MUST be present and valid       | §8.7    |
   | OEP-INV-004    | No chain gaps in BLOCKS/ directory                | §8.7    |
   | OEP-INV-005    | Public key embedded in KEYS/, not referenced      | §8.7    |
   | OEP-INV-006    | manifest_version MUST be "oep-1.0"                | §8.7    |
   | FEA-INV-001    | Platform private key never in HTTP request body   | §9.4    |
   | FEA-INV-002    | Every export logged before package returned       | §9.4    |
   | FEA-INV-003    | /export returns 401 without valid admin API key   | §9.4    |
   | FEA-INV-004    | /export returns 503 (fail-closed) with no key     | §9.4    |
   | FEA-INV-005    | FORENSIC_EXPORT_ALLOW_CALLER_KEYS forbidden prod  | §9.4    |
   | FVP-INV-007    | /verify response includes key_identity always     | §10.5   |

   Full ATF invariant stack across all three RFCs:

   | Family        | Invariants         | RFC       | Count |
   |---------------|--------------------|-----------|-------|
   | ATF-INV       | 001–006            | RFC-ATF-1 | 6     |
   | RGC-INV       | 001–008            | RFC-ATF-2 | 8     |
   | GPIL-INV      | 001–003            | RFC-ATF-3 | 3     |
   | ELR-INV       | 001–004            | RFC-ATF-3 | 4     |
   | EAP-INV       | 001–007            | RFC-ATF-3 | 7     |
   | OEP-INV       | 001–006            | RFC-ATF-3 | 6     |
   | FEA-INV       | 001–005            | RFC-ATF-3 | 5     |
   | FVP-INV       | 007                | RFC-ATF-3 | 1     |
   | TOTAL         |                    |           | 40    |


12.  Compliance Designations

12.1.  ATF-FEI-Compliant

   An implementation is ATF-FEI-Compliant if and only if it satisfies:

   (a) All six invariants of RFC-ATF-1 (ATF-INV-001–006).
   (b) All eight invariants of RFC-ATF-2 (RGC-INV-001–008).
   (c) All twenty-six invariants of RFC-ATF-3 (§11).
   (d) The GPIL Policy Parameter Registry bounds (§5.2).
   (e) The ELR evidence classification and retention matrix (§6.3).
   (f) The EAP pipeline trigger model including EMERGENCY_COLD (§7.7).
   (g) OEP generation using the Two-Phase Package Signing Protocol (§8.4).
   (h) FEA platform key resolution in the specified priority order (§9.2).
   (i) FVP key identity disclosure on all /verify responses (§10.1).
   (j) Verifier library determinism: pypqc only (§10.4).

   ATF-FEI-Compliant is the highest compliance designation in the ATF
   protocol stack as of Version 1.0.0.

12.2.  Compliance Hierarchy

   The full compliance hierarchy is:

   ATF-Compliant (RFC-ATF-1):
      Six invariants.  Cryptographic delegation, independent
      verifiability, and the Monotonic Authority Reduction guarantee.

   ATF-RGC-Compliant (RFC-ATF-1 + RFC-ATF-2):
      Fourteen invariants.  Adds continuous authority health monitoring,
      AFG, escalation protocol, and reauthorization challenge.

   ATF-GPI-Aligned (RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3 §5):
      Fourteen invariants + GPIL-INV-001–003 + established CRGC.
      Full Layer 1 + Layer 2 + Layer 3 interoperability — governance
      agreement between runtimes, not merely cryptographic validity.
      (Per-pair designation; see §5.5.)

   ATF-FEI-Compliant (RFC-ATF-1 + RFC-ATF-2 + RFC-ATF-3):
      Forty invariants.  Full Forensic Evidence Infrastructure: policy
      interoperability, evidence lifecycle management, immutable archive
      pipeline, forensic package format, authenticated export, and
      forensic verification protocol.


13.  Implementation Requirements

   The following infrastructure requirements apply to production
   ATF-FEI-Compliant deployments:

   | Requirement         | Reason                               | Non-compliance consequence            |
   |---------------------|--------------------------------------|---------------------------------------|
   | REDIS_URL           | Block ID sequencing (EAP-INV-007) +  | Block ID collisions in multi-process; |
   |                     | distributed rate limiting (§10.3)    | rate limits per-dyno, not per-IP      |
   | OMNIX_SIGNING_SECRET| OEP package signing (FEA-INV-004)    | /export returns 503; OEPs unsigned    |
   | _KEY_B64            |                                      |                                       |
   | OMNIX_SIGNING_PUBLIC| Key identity fingerprinting          | platform_fingerprint = null in all    |
   | _KEY_B64            | (FVP-INV-007)                        | /verify responses                     |
   | Object storage with | COLD tier (§6.2.3)                   | COLD tier unavailable; EMERGENCY_COLD |
   | object lock enabled | (S3-compatible)                      | cannot seal                           |

   The FORENSIC_EXPORT_ALLOW_CALLER_KEYS variable MUST NOT appear in
   any production environment configuration.  Its presence constitutes
   a violation of FEA-INV-005.

   The pypqc package (available as pypqc on PyPI) MUST be installed in
   every environment running omnix_atf_verify.py.  No alternative
   ML-DSA-65 library is permitted.

   The evidence_custody_log table MUST be created before any pipeline
   code runs.  It is a prerequisite, not an output.


14.  Security Considerations

14.1.  Key Identity Inversion Attack

   An adversary may construct a block signed with an arbitrary ML-DSA-65
   keypair, submit it to the /verify endpoint, receive a PASS verdict
   (the signature is valid against the provided key), and present that
   verdict as OMNIX platform endorsement.

   Mitigation: FVP-INV-007 (§10.5) requires every /verify response to
   include key_identity.matches_platform.  A UI or API consumer MUST
   treat matches_platform = false as a non-platform verification and
   MUST NOT present the PASS verdict as platform endorsement.  The
   warning field provides human-readable disambiguation.

14.2.  Block ID Collision in Distributed Deployments

   Without a globally synchronized sequence, two deployment processes
   sealing blocks simultaneously may produce blocks with identical IDs.
   Block ID collision breaks EAP-INV-003 (chain integrity) because the
   predecessor link becomes ambiguous.

   Mitigation: EAP-INV-007 requires Redis INCR as the block ID source
   in production.  Redis INCR is atomic; no collision is possible.  The
   in-process fallback emits a WARNING and is acceptable only in single-
   process dev/test environments.  If strict uniqueness is required
   even during Redis unavailability, implementations MAY choose to fail
   the seal operation rather than use the fallback.

14.3.  Archive Tampering and Chain Break

   An adversary with write access to COLD storage may attempt to modify
   an archived block — to suppress evidence, alter timestamps, or
   remove artifacts from the immutable record.

   Mitigation: The block chain (§7.5) ensures that any modification to
   any block invalidates every subsequent block's predecessor_block_hash
   link.  The omnix_atf_verify.py CLI (§7.6) detects this via
   CHAIN_BREAK verdict.  Object lock on the COLD storage tier prevents
   in-place modification.  The ML-DSA-65 signature on each block
   independently establishes the platform's attestation of block
   contents at seal time.

14.4.  Package Impersonation

   An adversary may attempt to generate an OEP purportedly from OMNIX
   QUANTUM using an arbitrary ML-DSA-65 keypair not associated with the
   platform.

   Mitigation: FEA-INV-001 (§9.4) requires that the platform key is
   read from the server environment — never from the caller — in
   production.  OEPs generated by the platform carry the platform's
   public key fingerprint in manifest.json.  A recipient can compare
   KEYS/public_key.b64 against the independently distributed platform
   public key to detect impersonation.

14.5.  Rate Limit Bypass via Auto-Scaling

   With in-memory rate limiting, a volumetric attack that triggers
   deployment auto-scaling simultaneously raises the effective rate
   limit (N dynos × configured limit).  The attack self-amplifies.

   Mitigation: §10.3 requires Redis-backed rate limiting in production.
   Redis counters are shared across all dynos, making the configured
   limit a true per-IP ceiling regardless of scale.

14.6.  Key Rotation and Public Key Registry

   RFC-ATF-3 does not specify a key rotation protocol.  When the
   platform ML-DSA-65 signing key is rotated:

   (a) All OEPs sealed before rotation remain verifiable against the
       old public key (embedded in each OEP's KEYS/public_key.b64).

   (b) All COLD blocks sealed before rotation retain their original
       signatures (EAP-INV-002 — signatures are untouchable).

   (c) A public key registry mapping key fingerprints to validity periods
       is RECOMMENDED for deployments that rotate keys.  Key rotation
       protocol specification is deferred to a future RFC-ATF extension.
       Active tracking: OMNIX-SEC-2026-001.


15.  References

   [RFC-ATF-1]
      Nunes, H., "RFC-ATF-1: Agent Trust Fabric Delegation Protocol,
      Version 1.0.0", OMNIX QUANTUM Open Standard, May 2026.
      DOI: 10.5281/zenodo.20155016
      SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6757339

   [RFC-ATF-2]
      Nunes, H., "RFC-ATF-2: Agent Trust Fabric — Runtime Governance
      Continuity, Version 1.0.0", OMNIX QUANTUM Open Standard, May 2026.
      SSRN: 6763978

   [FIPS204]
      National Institute of Standards and Technology, "Module-Lattice-
      Based Digital Signature Standard (ML-DSA)", FIPS 204, August 2024.

   [RFC2119]
      Bradner, S., "Key words for use in RFCs to Indicate Requirement
      Levels", BCP 14, RFC 2119, March 1997.

   [RFC8174]
      Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key
      Words", BCP 14, RFC 8174, May 2017.

   [ADR-161]
      Nunes, H., "Governance Policy Interoperability Layer (GPIL)",
      OMNIX ADR-161, May 2026.
      omnixquantum.net/docs/adr/ADR-161

   [ADR-162]
      Nunes, H., "Evidence Lifecycle & Immutable Retention",
      OMNIX ADR-162, May 2026.
      omnixquantum.net/docs/adr/ADR-162

   [ADR-163]
      Nunes, H., "Immutable Evidence Archive Pipeline",
      OMNIX ADR-163, May 2026.
      omnixquantum.net/docs/adr/ADR-163

   [ADR-165]
      Nunes, H., "OMNIX Evidence Package (OEP) Format",
      OMNIX ADR-165, May 2026.
      omnixquantum.net/docs/adr/ADR-165

   [ADR-166]
      Nunes, H., "Forensic Export Endpoint Authentication & Platform
      Key Pinning", OMNIX ADR-166, May 2026.
      omnixquantum.net/docs/adr/ADR-166

   [ADR-167]
      Nunes, H., "Forensic Layer Hardening: Key Identity Registry,
      Distributed Block Sequencing & Verifier Determinism",
      OMNIX ADR-167, May 2026.
      omnixquantum.net/docs/adr/ADR-167

   [ADR-156]
      Nunes, H., "Agent Trust Fabric", OMNIX ADR-156, 2026.
      omnixquantum.net/docs/adr/ADR-156

   [ADR-159]
      Nunes, H., "Runtime Governance Continuity", OMNIX ADR-159, 2026.
      omnixquantum.net/docs/adr/ADR-159

   [EDRM]
      Electronic Discovery Reference Model.
      edrm.net — forensic package design reference.

   [RFC1951]
      Deutsch, P., "DEFLATE Compressed Data Format Specification
      version 1.3", RFC 1951, May 1996.


16.  Appendix A — COLD Block Format Reference

   Field reference for OMNIX-BLOCK-{YYYYMMDD}-{seq:06d}.json:

   | Field                         | Type    | Required | Description                             |
   |-------------------------------|---------|----------|-----------------------------------------|
   | block_id                      | string  | REQUIRED | OMNIX-BLOCK-{YYYYMMDD}-{seq:06d}        |
   | creation_timestamp_ns         | integer | REQUIRED | Unix nanosecond timestamp of sealing    |
   | artifact_count                | integer | REQUIRED | Number of governance artifacts in block |
   | evidence_classes              | array   | REQUIRED | Distinct class codes present            |
   | canonical_hash                | string  | REQUIRED | sha256:{hex} of block content           |
   | predecessor_block_hash        | string  | REQUIRED | sha256:{hex} of prior block; or 0×64   |
   | integrity_manifest            | object  | REQUIRED | {artifact_hashes[], merkle_root, algo}  |
   | integrity_manifest.merkle_root| string  | REQUIRED | sha256:{hex} of sorted hash join        |
   | integrity_manifest.hash_algo  | string  | REQUIRED | "sha256-v1"                             |
   | pqc_signature                 | string  | REQUIRED | ML-DSA-65 sig over canonical_hash bytes |
   | pqc_algorithm                 | string  | REQUIRED | "ML-DSA-65 (FIPS 204)"                  |
   | omnix_version                 | string  | REQUIRED | Platform version at time of sealing     |


17.  Appendix B — OEP Directory Structure Reference

   | Path                                  | Required | Description                                 |
   |---------------------------------------|----------|---------------------------------------------|
   | META/manifest.json                    | REQUIRED | Signed package manifest (oep-1.0)           |
   | META/README.txt                       | REQUIRED | Human-readable verification instructions    |
   | BLOCKS/OMNIX-BLOCK-*.json             | REQUIRED | COLD blocks in chain order (1 or more)      |
   | BLOCKS/chain_index.json               | REQUIRED | [{block_id, canonical_hash, seq}]           |
   | KEYS/public_key.b64                   | REQUIRED | Issuer ML-DSA-65 public key, base64         |
   | VERIFY/omnix_atf_verify.py            | REQUIRED | Standalone offline CLI verifier (pypqc)     |
   | VERIFY/verify_all.sh                  | REQUIRED | Full chain verification shell script        |
   | CUSTODY/evidence_custody_log.json     | REQUIRED | Custody log for all blocks in package       |
   | REPORT/forensic_report.html           | REQUIRED | Self-contained offline forensic report      |
   | SIGNATURE/package_signature.json      | REQUIRED | ML-DSA-65 sig over canonical manifest hash  |


18.  Appendix C — FEI Compliance Checklist

   Implementations MUST satisfy all items to claim ATF-FEI-Compliant:

   GPIL
   □ Interoperability claims characterized using three-layer taxonomy (GPIL-INV-001)
   □ AFG_FRAGMENTATION_LIMIT in [0.01, 0.95]; startup rejection of >0.95 values (GPIL-INV-002)
   □ RGC_RC_TTL_SECONDS in [30, 3600] (GPIL-INV-002)
   □ CRGCs carry ML-DSA-65 signatures from all parties[] (GPIL-INV-003)
   □ CRGCs classified as CONTRACT evidence and stored immutably

   ELR
   □ Every artifact assigned to one of eight evidence classes at write time (§6.1)
   □ LEGAL/PQC/CONTRACT/EXCEPTION: never promoted to WARM, never deleted (ELR-INV-002)
   □ TELEMETRY/SAMPLE: HOT minimum 30 days (ELR-INV-004)
   □ Shadow event reduction applied at write time, not retroactively (§6.4)
   □ RCR classification table applied at write time (§6.5)
   □ Evidence class reclassification only upward, never downward (ELR-INV-003)

   EAP
   □ WARM manifest entry written before any transformation (EAP-INV-001, EAP-INV-006)
   □ pqc_signatures preserved verbatim in COLD blocks (EAP-INV-002)
   □ Block chain unbroken from genesis to head (EAP-INV-003)
   □ Immutable classes sealed complete in COLD — no field stripping (EAP-INV-004)
   □ Offline reconstructability verified: no platform dependency in verifier (EAP-INV-005)
   □ Block IDs use Redis INCR in production; in-process fallback emits WARNING (EAP-INV-007)
   □ EMERGENCY_COLD triggered on RGC-INV-003 HALT events (§7.7)
   □ evidence_custody_log table created before pipeline runs (§7.8)

   OEP
   □ .oep file is valid ZIP64 with anti-zip-slip protection (§8.1)
   □ All nine required paths present in the archive (§8.2)
   □ manifest_version = "oep-1.0" (OEP-INV-006)
   □ Every file listed in manifest.files[] with correct SHA-256 (OEP-INV-002)
   □ Two-phase signing protocol implemented (no circular reference) (§8.4)
   □ SIGNATURE/package_signature.json present and verifiable (OEP-INV-003)
   □ No chain gaps in BLOCKS/: all predecessor blocks present (OEP-INV-004)
   □ Public key embedded in KEYS/public_key.b64 (OEP-INV-005)
   □ forensic_report.html: no external dependencies; truncation notices shown (§8.6)

   FEA
   □ POST /api/forensic/export: admin API key required (FEA-INV-003)
   □ Platform key resolved from server environment, not request body (FEA-INV-001)
   □ Fail-closed 503 when no signing key available (FEA-INV-004)
   □ Export audit log entry written before package returned (FEA-INV-002)
   □ FORENSIC_EXPORT_ALLOW_CALLER_KEYS absent from production config (FEA-INV-005)

   FVP
   □ /verify response includes key_identity object always (FVP-INV-007)
   □ platform_fingerprint populated when OMNIX_SIGNING_PUBLIC_KEY_B64 is set (FVP-INV-007)
   □ Warning emitted when matches_platform = false; WARNING log entry created (§10.1)
   □ Rate limiting backed by Redis in production (§10.3)
   □ omnix_atf_verify.py uses pypqc only — no alternative library fallbacks (§10.4)
   □ omnix_atf_verify.py has zero imports from omnix_core or platform codebase (§10.4)

   General
   □ All RFC-ATF-1 invariants satisfied (ATF-INV-001–006)
   □ All RFC-ATF-2 invariants satisfied (RGC-INV-001–008)
   □ REDIS_URL configured in production (§13)
   □ OMNIX_SIGNING_SECRET_KEY_B64 and PUBLIC_KEY_B64 configured (§13)
   □ Object storage with object lock enabled for COLD tier (§13)
   □ pypqc installed in all verification environments (§13)


Author's Address

   Harold Nunes (Editor)
   OMNIX QUANTUM LTD
   United Kingdom
   Email: standards@omnixquantum.com

```
