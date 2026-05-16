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
 *   - Keys sorted lexicographically (recursive, matches Python sort_keys=True)
 *   - No spaces: compact JSON (separators=(",",":"))
 *   - Excluded fields filtered before hashing (RFC-ATF-1 §5.2)
 *   - SHA-256 of UTF-8 bytes, lowercase hex
 *
 * Nanosecond precision (BigInt safety):
 *   ATF receipts carry `_ns` fields (nanosecond epoch timestamps ~1.75e18)
 *   that exceed Number.MAX_SAFE_INTEGER (2^53 ≈ 9e15). JSON.parse() loses
 *   ~256 ns of precision for these values. When reading receipts from disk or
 *   wire, use computeContentHashFromString(rawJson) — it preserves exact
 *   nanosecond values for byte-identical hash parity with Python (FVP-INV-007).
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
 * Canonical serializer — compact JSON, keys sorted, BigInt emitted as integer.
 * Matches Python json.dumps(sort_keys=True, separators=(",",":")).
 */
function canonicalize(v: unknown): string {
  if (v === null) return 'null';
  if (typeof v === 'boolean') return String(v);
  if (typeof v === 'bigint') return String(v);   // BigInt → bare integer string (no quotes)
  if (typeof v === 'number') return String(v);
  if (typeof v === 'string') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonicalize).join(',') + ']';
  const obj = v as Record<string, unknown>;
  const pairs = Object.keys(obj)
    .sort()
    .map(k => JSON.stringify(k) + ':' + canonicalize(obj[k]));
  return '{' + pairs.join(',') + '}';
}

/**
 * Recompute the content_hash for any ATF receipt.
 *
 * @param receipt - The full receipt object (parsed JSON or constructed in code).
 *
 * WARNING: if the receipt was obtained via JSON.parse(str), any `_ns` fields
 * with values > 2^53 will have already lost nanosecond precision. Use
 * computeContentHashFromString(rawJson) to avoid this when reading from disk.
 *
 * @returns "sha256:<lowercase-hex-64>" — identical to Python reference.
 *
 * @example
 * const hash = computeContentHash(receipt);
 * assert(hash === receipt.content_hash); // ATF-INV-004
 */
export function computeContentHash(receipt: Record<string, unknown>): string {
  const filtered: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(receipt)) {
    if (!HASH_EXCLUDE_FIELDS.has(k)) filtered[k] = v;
  }
  return 'sha256:' + createHash('sha256').update(canonicalize(filtered), 'utf8').digest('hex');
}

/**
 * Recompute content_hash from a raw JSON string with nanosecond precision.
 *
 * Preferred over computeContentHash() when reading receipts from disk or wire.
 * Extracts _ns values at text level BEFORE JSON.parse(), stores them as BigInt,
 * then canonicalize() emits BigInt as bare integers — producing output
 * byte-identical to Python's json.dumps (FVP-INV-007).
 *
 * @param rawJson - Raw JSON string (e.g. from fs.readFileSync(path, 'utf8')).
 *
 * @example
 * const rawJson = fs.readFileSync('receipt.json', 'utf8');
 * const hash = computeContentHashFromString(rawJson);
 * assert(hash === parsedReceipt.content_hash); // ATF-INV-004
 */
export function computeContentHashFromString(rawJson: string): string {
  // Step 1: Extract _ns values BEFORE JSON.parse loses precision.
  // JS float64 can only represent integers exactly up to 2^53 = 9_007_199_254_740_992.
  // ATF epoch-ns timestamps for 2026 are ~1.75e18 >> 2^53, causing ~256 ns error.
  const NS_PATTERN = /"(\w+_ns)"\s*:\s*(\d+)/g;
  const nsValues = new Map<string, bigint>();
  let m: RegExpExecArray | null;
  while ((m = NS_PATTERN.exec(rawJson)) !== null) {
    const n = BigInt(m[2]);
    if (n > BigInt(Number.MAX_SAFE_INTEGER)) nsValues.set(m[1], n);
  }

  // Step 2: Parse (rounded _ns values will be patched in step 3).
  const obj = JSON.parse(rawJson) as Record<string, unknown>;

  // Step 3: Restore precise BigInt values for high-ns fields.
  for (const [k, v] of nsValues) {
    if (k in obj) (obj as Record<string, unknown>)[k] = v;
  }

  // Step 4: computeContentHash handles BigInt via canonicalize().
  return computeContentHash(obj);
}
