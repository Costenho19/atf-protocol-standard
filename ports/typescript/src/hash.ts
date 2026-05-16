/**
   * Canonical JSON + SHA-256 for ATF content hash (ATF-INV-004, FVP-INV-007).
   *
   * Produces byte-identical output to the Python reference:
   *
   *   payload = {k: v for k, v in receipt.items() if k not in EXCLUDE_FIELDS}
   *   canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
   *                          ensure_ascii=False)
   *   return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
   *
   * Key invariants:
   *   - Keys sorted lexicographically (recursive for nested objects)
   *   - No spaces in output: JSON.stringify with no replacer spaces
   *   - Excluded fields filtered before hashing
   *   - SHA-256 of UTF-8 bytes, lowercase hex
   */

  import { createHash } from 'crypto';

  /** Fields excluded from content_hash computation (RFC-ATF-1 §5.2, normative). */
  export const HASH_EXCLUDE_FIELDS = new Set([
    'content_hash',
    'pqc_signature',
    'pqc_algorithm',
    '_comment',
    '_ces_formula',
    '_test_note',
  ]);

  /**
   * Sort all object keys recursively, preserve array order.
   * Matches Python's json.dumps(sort_keys=True) behaviour.
   */
  function sortValue(v: unknown): unknown {
    if (v === null || typeof v !== 'object') return v;
    if (Array.isArray(v)) return v.map(sortValue);
    const obj = v as Record<string, unknown>;
    const sorted: Record<string, unknown> = {};
    for (const k of Object.keys(obj).sort()) {
      sorted[k] = sortValue(obj[k]);
    }
    return sorted;
  }

  /**
   * Recompute the content_hash for any ATF receipt.
   *
   * @param receipt - The full receipt object (parsed JSON).
   * @returns `"sha256:<lowercase-hex>"` — identical to Python reference for same input.
   *
   * @example
   * const hash = computeContentHash(receipt);
   * assert(hash === receipt.content_hash); // ATF-INV-004
   */
  export function computeContentHash(receipt: Record<string, unknown>): string {
    // Step 1 — Filter excluded fields
    const filtered: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(receipt)) {
      if (!HASH_EXCLUDE_FIELDS.has(k)) {
        filtered[k] = v;
      }
    }

    // Step 2 — Sort keys recursively
    const sorted = sortValue(filtered) as Record<string, unknown>;

    // Step 3 — Canonical JSON: compact (no spaces)
    // JSON.stringify with no space arg produces compact output matching Python separators=(",",":")
    const canonical = JSON.stringify(sorted);

    // Step 4 — SHA-256, lowercase hex
    const digest = createHash('sha256').update(canonical, 'utf8').digest('hex');
    return `sha256:${digest}`;
  }
  