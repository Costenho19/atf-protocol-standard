# Security Policy — ATF Protocol Standard

  ## Supported Versions

  | Version | RFC | Status | Security Support |
  |---|---|---|---|
  | v3.0.0 | RFC-ATF-3 | **Current** | ✅ Active |
  | v2.0.0 | RFC-ATF-2 | Maintained | ✅ Active |
  | v1.0.0 | RFC-ATF-1 | Maintained | ✅ Active |

  All supported versions receive security advisories and errata. Older patch versions are superseded by the current release.

  ---

  ## Cryptographic Policy

  | Property | Value |
  |---|---|
  | **Signing Algorithm** | ML-DSA-65 (Dilithium-3, FIPS 204) |
  | **Security Level** | NIST Level 3 — 128-bit post-quantum security |
  | **Hash Algorithm** | SHA-256 (content hash) |
  | **Key Format** | Base64-encoded ML-DSA-65 keypair |
  | **Signature Coverage** | content_hash field — all excluded fields are protocol-defined |
  | **Offline Verifiability** | Required by EAP-INV-005 — no platform trust required |

  ### Cryptographic Limitations

  1. **Clock Trust:** TAR admission timestamps rely on the local system clock. ATF does not specify a trusted time source — implementations SHOULD use NTP with authentication or HSM timestamping.
  2. **Revocation Propagation:** ATF does not define a real-time revocation protocol. HALT status propagates within an execution session; inter-session revocation requires out-of-band coordination.
  3. **Key Rotation:** ATF receipts are signed with the key active at issuance. Key rotation does not retroactively invalidate prior receipts — this is a design property, not a limitation.

  ---

  ## Threat Model Summary

  | ID | Threat | ATF Mitigation |
  |---|---|---|
  | TM-001 | Unauthorized agent authority expansion | ATF-INV-001 (MAR) — enforced cryptographically |
  | TM-002 | Receipt tampering post-issuance | content_hash + PQC signature — ATF-INV-004 |
  | TM-003 | Authority chain forgery | chain_root_id + delegation_depth — ATF-INV-003 |
  | TM-004 | Expired delegation reuse | TAR admission timestamp check — ATF-INV-006 |
  | TM-005 | CES score manipulation | RGC-INV-002 — formula is fixed, not configurable |
  | TM-006 | HALT suppression | RGC-INV-004 — HALT propagates atomically |
  | TM-007 | Evidence archive tampering | Merkle-chained ARH + PQC signature — EAP-INV-001 |
  | TM-008 | Unauthorized forensic export | FEA-INV-001–005 — export authentication required |
  | TM-009 | Verifier non-determinism | FVP-INV-007 — same key + same evidence = same result |

  ---

  ## Hardening Guidelines by Deployment Context

  ### Production (Cloud / On-Premises)
  - Store ML-DSA-65 private keys in an HSM or KMS with audit logging
  - Set `OMNIX_ANTI_REPLAY_MODE=strict`
  - Do NOT set `AVM_AUTO_APPROVE=true` — disables the AMG approval gate
  - Do NOT set `FORENSIC_EXPORT_ALLOW_CALLER_KEYS=true` — FEA-INV-005 violation
  - Configure `ADMIN_ALLOWED_IPS` to restrict admin endpoints
  - Use Redis with TLS for anti-replay state

  ### Regulatory / Forensic Contexts
  - Enable HOT→WARM→COLD lifecycle transitions (ELR-INV-001–004)
  - Retain COLD-tier evidence for ≥7 years per ELR-INV-004
  - Verify OEP packages are self-contained before archival (OEP-INV-001)
  - Maintain key custody chain documentation alongside COLD archives

  ### Development / Testing
  - Use `TESTING=true` ONLY in development — disables AVM scheduler and alerts
  - Generate ephemeral keypairs for local development
  - Never use production keys in development environments

  ---

  ## Reporting a Vulnerability

  **Contact:** security@omnixquantum.com

  **PGP:** Available on request from standards@omnixquantum.com

  **Response SLA:**

  | Severity | Acknowledgement | Triage | Resolution |
  |---|---|---|---|
  | Critical (P0) | 24 hours | 48 hours | 7 days |
  | High (P1) | 48 hours | 72 hours | 30 days |
  | Medium (P2) | 5 days | 10 days | 90 days |
  | Low (P3) | 10 days | 30 days | Next release |

  **Severity criteria:**

  - **Critical:** Cryptographic break, MAR bypass, HALT suppression, evidence forgery
  - **High:** Verifier non-determinism, CES formula manipulation, unauthorized export
  - **Medium:** Clock manipulation attacks, partial revocation bypass
  - **Low:** Documentation inconsistencies, minor invariant ambiguities

  **Disclosure policy:** We follow coordinated disclosure. Please do not publicly disclose vulnerabilities before a fix is available and agreed upon.

  ---

  ## Protocol Invariant Security Properties

  The 40 ATF invariants are security properties, not implementation guidelines. Any deviation from an invariant constitutes a security violation, not a configuration choice.

  Security-critical invariants (non-negotiable):

  | Invariant | Property | Consequence of violation |
  |---|---|---|
  | ATF-INV-001 (MAR) | Authority monotonicity | Privilege escalation |
  | ATF-INV-004 | Signature integrity | Receipt forgery |
  | ATF-INV-005 | Offline verifiability | Audit capture failure |
  | RGC-INV-002 | CES formula integrity | Continuity score manipulation |
  | RGC-INV-004 | HALT propagation | Unauthorized continued execution |
  | EAP-INV-001 | Archive chain integrity | Evidence tampering |
  | FVP-INV-007 | Verifier determinism | Inconsistent audit outcomes |

  ---

  *OMNIX QUANTUM LTD · security@omnixquantum.com*
  *Protocol maintained under CC BY 4.0 — security reports handled confidentially*
  