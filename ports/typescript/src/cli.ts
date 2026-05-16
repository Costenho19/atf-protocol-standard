#!/usr/bin/env node
  /**
   * ATF Protocol Verifier CLI — @atf-protocol/verifier
   *
   * Usage:
   *   npx atf-verify receipt.json
   *   npx atf-verify receipt.json --verbose
   *   npx atf-verify receipt.json --public-key key.b64
   */

  import * as fs   from 'fs';
  import * as path from 'path';
  import { verifyReceipt } from './verifier';

  const args = process.argv.slice(2);
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
  ATF Protocol Offline Verifier — @atf-protocol/verifier
  RFC-ATF-1 / RFC-ATF-2 / RFC-ATF-3

  Usage:
    npx atf-verify <receipt.json> [--verbose] [--public-key <key.b64>]

  Examples:
    npx atf-verify delegation_receipt.json
    npx atf-verify runtime_continuity_record.json --verbose
    npx atf-verify receipt.json --public-key my_public_key.b64

  Protocol: https://costenho19.github.io/atf-protocol-standard/
  `);
    process.exit(0);
  }

  const filePath  = args[0];
  const verbose   = args.includes('--verbose');
  const pkIdx     = args.indexOf('--public-key');
  const publicKey = pkIdx !== -1 ? args[pkIdx + 1] : undefined;

  let receipt: Record<string, unknown>;
  try {
    const raw = fs.readFileSync(path.resolve(filePath), 'utf8');
    receipt = JSON.parse(raw);
  } catch (e) {
    console.error(`Error reading ${filePath}: ${(e as Error).message}`);
    process.exit(1);
  }

  const result = verifyReceipt(receipt, publicKey ? { publicKeyB64: publicKey } : {});

  console.log(`\nATF Receipt Verification\n──────────────────────────────────────────────────`);
  console.log(`Receipt ID  : ${result.receiptId || '(unknown)'}`);
  console.log(`Type        : ${result.receiptType}`);
  console.log(`Verdict     : ${result.verdict === 'PASS' ? '✓ PASS' : '✗ FAIL'}`);
  console.log(``);
  console.log('Checks:');

  for (const [key, check] of Object.entries(result.checks)) {
    const icon = check.ok ? '  ✓' : '  ✗';
    const note = verbose ? ` — ${check.note ?? ''}` : '';
    console.log(`${icon} ${key}${note}`);
  }

  if (result.notes.length > 0 && verbose) {
    console.log(`\nNotes:`);
    result.notes.forEach(n => console.log(`  ${n}`));
  }

  console.log(``);
  process.exit(result.verdict === 'PASS' ? 0 : 1);
  