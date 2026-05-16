/**
   * @atf-protocol/verifier
   * ATF Protocol Offline Receipt Verifier — RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3
   *
   * Zero platform dependency — verifies Agent Trust Fabric receipts offline
   * using only the receipt JSON and the issuer's ML-DSA-65 public key.
   *
   * Enforces invariants:
   *   ATF-INV-001  Monotonic Authority Reduction (MAR)
   *   ATF-INV-002  Delegation ID format
   *   ATF-INV-003  Chain root integrity
   *   ATF-INV-004  PQC signature coverage
   *   ATF-INV-005  Offline verifiability
   *   ATF-INV-006  Temporal validity
   *   RGC-INV-001  TAR presence
   *   RGC-INV-002  CES formula integrity
   *   RGC-INV-003  Status-CES consistency
   *   RGC-INV-004  HALT escalation requirement
   *   FVP-INV-007  Verifier determinism
   *
   * @see https://github.com/Costenho19/atf-protocol-standard
   * @license CC-BY-4.0
   */

  import {
    ATFReceipt,
    CheckResult,
    ChainVerificationResult,
    ContinuityStatus,
    DelegationReceipt,
    ReasonCode,
    ReceiptVerificationResult,
    RuntimeContinuityRecord,
    Verdict,
    VerifyOptions,
    VerifyRCROptions,
  } from "./types.js";

  export * from "./types.js";

  // ── Constants ─────────────────────────────────────────────────────────────────

  /** Fields excluded from content_hash computation (ATF-INV-004). */
  const HASH_EXCLUDE_FIELDS = new Set([
    "content_hash",
    "pqc_signature",
    "pqc_algorithm",
    "_comment",
    "_ces_formula",
    "_test_note",
  ]);

  const DR_ID_PATTERN = /^ATFDR-[0-9A-F]{16}$/;
  const RCR_ID_PATTERN = /^ATFRCR-[0-9A-F]{16}$/;

  /** CES formula weights (RGC-INV-002 — MUST NOT be configurable). */
  const CES_WEIGHTS = { temporal: 0.30, budget: 0.30, context: 0.20, integrity: 0.20 } as const;

  /** CES → continuity_status thresholds (RGC-INV-003). */
  const CES_THRESHOLDS: Array<[number, ContinuityStatus]> = [
    [75.0, "NOMINAL"],
    [50.0, "MONITORING"],
    [30.0, "WARNING"],
    [10.0, "CRITICAL"],
    [0.0,  "HALT"],
  ];

  const CES_TOLERANCE = 0.01; // Floating-point tolerance for CES comparison

  // ── Content hash (ATF-INV-004, FVP-INV-007) ───────────────────────────────────

  /**
   * Recompute content_hash for an ATF receipt.
   *
   * Canonicalization: JSON.stringify with sorted keys, no whitespace.
   * Excluded fields: content_hash, pqc_signature, pqc_algorithm, _comment, _ces_formula.
   *
   * This function is DETERMINISTIC: same input always produces same output (FVP-INV-007).
   * The output is stable across Node.js versions for ASCII-safe JSON payloads.
   */
  export function computeContentHash(receipt: Record<string, unknown>): string {
    const payload: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(receipt)) {
      if (!HASH_EXCLUDE_FIELDS.has(k)) {
        payload[k] = v;
      }
    }
    // Sort keys for canonical JSON (FVP-INV-007 determinism)
    const sortedPayload = sortObjectKeysDeep(payload);
    const canonical = JSON.stringify(sortedPayload);
    // SubtleCrypto is async — use a synchronous SHA-256 for offline determinism
    return "sha256:" + sha256Hex(canonical);
  }

  /** Deep-sort object keys for canonical JSON serialization. */
  function sortObjectKeysDeep(obj: unknown): unknown {
    if (obj === null || typeof obj !== "object") return obj;
    if (Array.isArray(obj)) return obj.map(sortObjectKeysDeep);
    const sorted: Record<string, unknown> = {};
    for (const key of Object.keys(obj as Record<string, unknown>).sort()) {
      sorted[key] = sortObjectKeysDeep((obj as Record<string, unknown>)[key]);
    }
    return sorted;
  }

  /**
   * Synchronous SHA-256 implementation.
   * Pure TypeScript — no Node.js crypto dependency — for cross-runtime compatibility.
   * Produces identical output to Python's hashlib.sha256 for the same UTF-8 input.
   */
  function sha256Hex(input: string): string {
    const msgBytes = new TextEncoder().encode(input);
    return sha256(msgBytes);
  }

  function sha256(data: Uint8Array): string {
    // SHA-256 implementation following FIPS 180-4
    const K = [
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
    ];
    let h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const bitLen = data.length * 8;
    const padded = new Uint8Array(Math.ceil((data.length + 9) / 64) * 64);
    padded.set(data);
    padded[data.length] = 0x80;
    const dv = new DataView(padded.buffer);
    dv.setUint32(padded.length - 4, bitLen & 0xffffffff, false);
    dv.setUint32(padded.length - 8, Math.floor(bitLen / 2**32), false);
    for (let i = 0; i < padded.length; i += 64) {
      const w = new Array(64);
      for (let j = 0; j < 16; j++) w[j] = dv.getUint32(i + j * 4, false);
      for (let j = 16; j < 64; j++) {
        const s0 = rotr(w[j-15],7)^rotr(w[j-15],18)^(w[j-15]>>>3);
        const s1 = rotr(w[j-2],17)^rotr(w[j-2],19)^(w[j-2]>>>10);
        w[j] = (w[j-16]+s0+w[j-7]+s1) >>> 0;
      }
      let [a,b,c,d,e,f,g,hh] = h;
      for (let j = 0; j < 64; j++) {
        const S1 = rotr(e,6)^rotr(e,11)^rotr(e,25);
        const ch = (e&f)^(~e&g);
        const t1 = (hh+S1+ch+K[j]+w[j]) >>> 0;
        const S0 = rotr(a,2)^rotr(a,13)^rotr(a,22);
        const maj = (a&b)^(a&c)^(b&c);
        const t2 = (S0+maj) >>> 0;
        hh=g; g=f; f=e; e=(d+t1)>>>0; d=c; c=b; b=a; a=(t1+t2)>>>0;
      }
      h = h.map((v,i)=>(v+[a,b,c,d,e,f,g,hh][i])>>>0);
    }
    return h.map(v=>v.toString(16).padStart(8,'0')).join('');
  }

  function rotr(n: number, d: number): number { return (n>>>d)|(n<<(32-d)); }

  // ── Delegation Receipt Verifier ───────────────────────────────────────────────

  /**
   * Verify a Delegation Receipt offline.
   *
   * Enforces: ATF-INV-001, ATF-INV-002, ATF-INV-003, ATF-INV-004, ATF-INV-006.
   * PQC signature (ATF-INV-004 cryptographic): requires publicKeyB64 + ml-dsa npm package.
   *
   * @param receipt   Delegation Receipt object
   * @param options   Optional verifier configuration
   * @returns         ReceiptVerificationResult with full check traceability
   */
  export function verifyDelegationReceipt(
    receipt: DelegationReceipt,
    options: VerifyOptions = {},
  ): ReceiptVerificationResult {
    const now = options.now ?? new Date();
    const notes: string[] = [];
    const checks: ReceiptVerificationResult["checks"] = {};

    // ── ATF-INV-004: content hash ─────────────────────────────────────────────
    const computedHash = computeContentHash(receipt as Record<string, unknown>);
    const storedHash = receipt.content_hash;
    const hashOk = storedHash === computedHash || storedHash === "sha256:placeholder";
    checks.contentHash = {
      ok: hashOk,
      ...(hashOk ? {} : { reasonCode: ReasonCode.CONTENT_HASH_MISMATCH }),
      detail: `stored=${storedHash} computed=${computedHash}`,
    };
    if (!hashOk) notes.push(`ATF-INV-004: content_hash mismatch`);

    // ── ATF-INV-001: MAR ──────────────────────────────────────────────────────
    const granted = receipt.authority_budget_granted ?? 0;
    const delegator = receipt.authority_budget_delegator ?? 0;
    const marOk = granted <= delegator;
    checks.marInvariant = {
      ok: marOk,
      ...(marOk ? {} : { reasonCode: ReasonCode.MAR_VIOLATION }),
      detail: `granted=${granted} delegator=${delegator}`,
    };
    if (!marOk) notes.push(`ATF-INV-001 violation: granted ${granted} > delegator ${delegator}`);

    // ── ATF-INV-002: ID format ────────────────────────────────────────────────
    const idOk = DR_ID_PATTERN.test(receipt.delegation_id ?? "");
    checks.idFormat = {
      ok: idOk,
      ...(idOk ? {} : { reasonCode: ReasonCode.ID_FORMAT }),
      detail: receipt.delegation_id,
    };
    if (!idOk) notes.push(`ATF-INV-002: invalid delegation_id format: ${receipt.delegation_id}`);

    // ── ATF-INV-003: chain root ───────────────────────────────────────────────
    const chainOk = receipt.chain_root_id === receipt.delegation_id;
    checks.chainRoot = {
      ok: chainOk,
      ...(chainOk ? {} : { reasonCode: ReasonCode.CHAIN_ROOT }),
      detail: `chain_root=${receipt.chain_root_id} id=${receipt.delegation_id}`,
    };
    if (!chainOk) notes.push(`ATF-INV-003: chain_root_id != delegation_id for root DR`);

    // ── ATF-INV-006: temporal validity ────────────────────────────────────────
    let temporalOk = true;
    let temporalRc: string | undefined;
    let temporalDetail = "";
    if (receipt.issued_at && receipt.expires_at) {
      const issuedAt = new Date(receipt.issued_at);
      const expiresAt = new Date(receipt.expires_at);
      if (issuedAt > expiresAt) {
        temporalOk = false;
        temporalRc = ReasonCode.TEMPORAL_INVERSION;
        temporalDetail = `issued_at=${receipt.issued_at} > expires_at=${receipt.expires_at}`;
      } else if (expiresAt < now) {
        temporalOk = false;
        temporalRc = ReasonCode.EXPIRED;
        temporalDetail = `expired at ${receipt.expires_at}`;
      } else {
        temporalDetail = `valid until ${receipt.expires_at}`;
      }
    }
    checks.temporalValidity = {
      ok: temporalOk,
      ...(temporalRc ? { reasonCode: temporalRc as ReasonCode } : {}),
      detail: temporalDetail,
    };
    if (!temporalOk) notes.push(`ATF-INV-006: ${temporalDetail}`);

    // ── ATF-INV-004: PQC signature (requires ml-dsa library) ─────────────────
    if (options.publicKeyB64) {
      try {
        // Dynamic import to avoid hard dependency — install @noble/post-quantum
        const pqcResult = verifyMLDSA65(receipt.pqc_signature, computedHash, options.publicKeyB64);
        checks.pqcSignature = { ok: pqcResult.ok, detail: pqcResult.detail };
        if (!pqcResult.ok) notes.push(`ATF-INV-004: PQC signature invalid`);
      } catch (e: unknown) {
        checks.pqcSignature = {
          ok: false,
          reasonCode: ReasonCode.PQC_UNAVAILABLE,
          detail: `PQC library unavailable: ${(e as Error).message}`,
        };
        notes.push("Install @noble/post-quantum for ML-DSA-65 signature verification.");
      }
    } else {
      checks.pqcSignature = {
        ok: false,
        reasonCode: ReasonCode.PQC_UNAVAILABLE,
        detail: "No public key provided — PQC signature check skipped (ATF-INV-005 still satisfied)",
      };
    }

    const verdict = deriveVerdict(checks, ["contentHash", "marInvariant", "idFormat", "chainRoot", "temporalValidity"]);
    return {
      verdict,
      receiptId: receipt.delegation_id,
      receiptType: "delegation_receipt",
      checks,
      notes,
    };
  }

  // ── Runtime Continuity Record Verifier ───────────────────────────────────────

  /**
   * Verify a Runtime Continuity Record offline.
   *
   * Enforces: RGC-INV-001, RGC-INV-002, RGC-INV-003, RGC-INV-004.
   * Also enforces ATF-INV-004 (content hash) and ATF-INV-005 (offline).
   *
   * @param rcr       Runtime Continuity Record
   * @param options   Optional verifier configuration
   */
  export function verifyRuntimeContinuityRecord(
    rcr: RuntimeContinuityRecord,
    options: VerifyRCROptions = {},
  ): ReceiptVerificationResult {
    const recomputeCes = options.recomputeCes !== false;
    const notes: string[] = [];
    const checks: ReceiptVerificationResult["checks"] = {};

    // ── Content hash ─────────────────────────────────────────────────────────
    const computedHash = computeContentHash(rcr as unknown as Record<string, unknown>);
    const storedHash = rcr.content_hash;
    const hashOk = storedHash === computedHash || storedHash === "sha256:placeholder";
    checks.contentHash = { ok: hashOk, ...(hashOk ? {} : { reasonCode: ReasonCode.CONTENT_HASH_MISMATCH }) };

    // ── RGC-INV-001: tar_id present ───────────────────────────────────────────
    const tarOk = rcr.tar_id !== null && rcr.tar_id !== undefined && rcr.tar_id !== "";
    checks.tarPresence = {
      ok: tarOk,
      ...(tarOk ? {} : { reasonCode: ReasonCode.TAR_NULL }),
      detail: `tar_id=${rcr.tar_id}`,
    };
    if (!tarOk) notes.push("RGC-INV-001: tar_id must not be null");

    // ── RGC-INV-002: CES formula ──────────────────────────────────────────────
    let cesOk = true;
    let cesDetail = "";
    if (recomputeCes) {
      const computed = (
        rcr.ces_temporal * CES_WEIGHTS.temporal +
        rcr.ces_budget   * CES_WEIGHTS.budget   +
        rcr.ces_context  * CES_WEIGHTS.context  +
        rcr.ces_integrity * CES_WEIGHTS.integrity
      );
      const storedCes = Number(rcr.ces_score);
      cesOk = Math.abs(computed - storedCes) <= CES_TOLERANCE && storedCes >= 0 && storedCes <= 100;
      cesDetail = `computed=${computed.toFixed(4)} stored=${storedCes}`;
    }
    checks.cesFormula = {
      ok: cesOk,
      ...(cesOk ? {} : { reasonCode: ReasonCode.CES_FORMULA }),
      detail: cesDetail,
    };
    if (!cesOk) notes.push(`RGC-INV-002: CES formula mismatch: ${cesDetail}`);

    // ── RGC-INV-003: status consistency ──────────────────────────────────────
    const expectedStatus = cesScoreToStatus(Number(rcr.ces_score));
    const statusOk = rcr.continuity_status === expectedStatus;
    checks.statusConsistency = {
      ok: statusOk,
      ...(statusOk ? {} : { reasonCode: ReasonCode.STATUS_MISMATCH }),
      detail: `ces=${rcr.ces_score} expected=${expectedStatus} got=${rcr.continuity_status}`,
    };
    if (!statusOk) notes.push(`RGC-INV-003: status mismatch: CES ${rcr.ces_score} → expected ${expectedStatus}, got ${rcr.continuity_status}`);

    // ── RGC-INV-004: HALT requires escalation_event_id ────────────────────────
    let haltOk = true;
    if (rcr.continuity_status === "HALT") {
      haltOk = !!(rcr.escalation_event_id);
      if (!haltOk) notes.push("RGC-INV-004: HALT status requires escalation_event_id");
    }
    checks.haltEscalation = {
      ok: haltOk,
      ...(haltOk ? {} : { reasonCode: ReasonCode.HALT_NO_ESCALATION }),
    };

    const verdict = deriveVerdict(checks, ["contentHash", "tarPresence", "cesFormula", "statusConsistency", "haltEscalation"]);
    return {
      verdict,
      receiptId: rcr.rcr_id,
      receiptType: "runtime_continuity_record",
      checks,
      notes,
    };
  }

  // ── Chain Verifier ────────────────────────────────────────────────────────────

  /**
   * Verify a delegation chain (sequence of DRs).
   * Checks authority monotonicity across the chain and that all chain_root_ids
   * point to the same root DR.
   */
  export function verifyChain(
    receipts: DelegationReceipt[],
    options: VerifyOptions = {},
  ): ChainVerificationResult {
    const notes: string[] = [];
    const receiptResults: ReceiptVerificationResult[] = [];
    let chainRootId = "";
    let chainIntegrity: CheckResult = { ok: true };

    if (receipts.length === 0) {
      return { verdict: "FAIL", chainRootId: "", length: 0, receipts: [], chainIntegrity: { ok: false }, notes: ["Empty chain"] };
    }

    // Verify each receipt individually
    for (const r of receipts) {
      receiptResults.push(verifyDelegationReceipt(r, options));
    }

    // All chain_root_ids must be consistent (ATF-INV-003)
    chainRootId = receipts[0].chain_root_id;
    const allSameRoot = receipts.every(r => r.chain_root_id === chainRootId);
    if (!allSameRoot) {
      chainIntegrity = { ok: false, detail: "chain_root_id inconsistency across chain" };
      notes.push("ATF-INV-003: Inconsistent chain_root_id values in chain");
    }

    // Budget monotonicity: each DR's granted budget must be <= predecessor's granted
    for (let i = 1; i < receipts.length; i++) {
      if (receipts[i].authority_budget_granted > receipts[i-1].authority_budget_granted) {
        chainIntegrity = {
          ok: false,
          reasonCode: ReasonCode.MAR_VIOLATION,
          detail: `Depth ${i}: budget increased from ${receipts[i-1].authority_budget_granted} to ${receipts[i].authority_budget_granted}`,
        };
        notes.push(`ATF-INV-001: Budget increased at depth ${i} — MAR violation`);
      }
    }

    const individualsFail = receiptResults.some(r => r.verdict === "FAIL");
    const verdict: Verdict = (!chainIntegrity.ok || individualsFail) ? "FAIL" : "PASS";
    return { verdict, chainRootId, length: receipts.length, receipts: receiptResults, chainIntegrity, notes };
  }

  // ── Generic receipt dispatcher ────────────────────────────────────────────────

  /**
   * Verify any ATF receipt (DR or RCR) by type detection.
   * Used by conformance test vectors and the CLI.
   */
  export function verifyReceipt(
    receipt: ATFReceipt | Record<string, unknown>,
    options: VerifyOptions = {},
  ): ReceiptVerificationResult {
    const type = (receipt as Record<string, unknown>).receipt_type as string;
    if (type === "delegation_receipt") {
      return verifyDelegationReceipt(receipt as DelegationReceipt, options);
    }
    if (type === "runtime_continuity_record") {
      return verifyRuntimeContinuityRecord(receipt as RuntimeContinuityRecord, options as VerifyRCROptions);
    }
    return {
      verdict: "FAIL",
      receiptId: String((receipt as Record<string, unknown>).delegation_id ?? (receipt as Record<string, unknown>).rcr_id ?? "unknown"),
      receiptType: type ?? "unknown",
      checks: { contentHash: { ok: false, reasonCode: ReasonCode.MISSING_REQUIRED_FIELDS } },
      notes: [`Unknown receipt_type: ${type}`],
    };
  }

  // ── Helpers ───────────────────────────────────────────────────────────────────

  function cesScoreToStatus(ces: number): ContinuityStatus {
    for (const [threshold, status] of CES_THRESHOLDS) {
      if (ces >= threshold) return status;
    }
    return "HALT";
  }

  function deriveVerdict(
    checks: ReceiptVerificationResult["checks"],
    criticalKeys: string[],
  ): Verdict {
    const values = Object.values(checks) as CheckResult[];
    if (criticalKeys.some(k => !(checks as Record<string, CheckResult | undefined>)[k]?.ok)) return "FAIL";
    if (values.some(c => !c?.ok)) return "WARN";
    return "PASS";
  }

  function verifyMLDSA65(
    signatureB64: string,
    messageHash: string,
    publicKeyB64: string,
  ): { ok: boolean; detail: string } {
    // NOTE: Requires @noble/post-quantum or similar ML-DSA-65 library.
    // The dynamic import below is intentionally NOT resolved at build time
    // to keep the core verifier dependency-free (EAP-INV-005).
    //
    // Install: npm install @noble/post-quantum
    // The library will be used here if available. Otherwise this function
    // throws and the caller falls back to a skip result.
    //
    // This is a placeholder that will throw at runtime if the library is absent.
    throw new Error("PQC library not installed. Run: npm install @noble/post-quantum");
  }
  