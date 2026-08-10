#!/usr/bin/env node
/**
 * Fail the build if this module has edited its vendored copy of the shared viewer.
 *
 * The viewer is owned by digital-3d-shared-contracts and vendored here by
 * tools/sync_viewer_ui.mjs, which writes viewer/shared/VIEWER-UI.sha256 alongside the files. This
 * script recomputes those hashes. It needs nothing but this repository, so it runs in CI whether or
 * not the shared repository is checked out — which matters, because the schema validator already
 * has to skip for exactly that reason and a control that skips is not a control.
 *
 * Three outcomes:
 *   in sync      exit 0
 *   drifted      exit 1, naming every file that differs
 *   not vendored exit 1, unless the repository declares itself unmigrated in viewer/shared.lock.json
 *
 * The unmigrated escape hatch exists so a module can be adopted deliberately rather than having its
 * deploy broken the moment this lands. It must name a tracking issue, and it prints loudly every
 * build, so it cannot quietly become permanent.
 */
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, posix, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SHARED = join(ROOT, 'viewer', 'shared');
const MANIFEST = join(SHARED, 'VIEWER-UI.sha256');
const LOCK = join(ROOT, 'viewer', 'shared.lock.json');

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const canonical = (buf) => Buffer.from(buf.toString('utf8').replace(/\r\n/g, '\n'), 'utf8');

function walk(dir, base = dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full, base));
    else out.push(posix.join(...relative(base, full).split(/[\\/]/)));
  }
  return out.sort();
}

function unmigrated(reason) {
  if (!existsSync(LOCK)) return false;
  const lock = JSON.parse(readFileSync(LOCK, 'utf8'));
  if (lock.adopted !== false) return false;
  console.warn('');
  console.warn('  ! SHARED VIEWER NOT ADOPTED');
  console.warn(`    ${reason}`);
  console.warn(`    reason:   ${lock.reason ?? '(none given)'}`);
  console.warn(`    tracking: ${lock.tracking_issue ?? '(none given)'}`);
  console.warn('    This module still carries its own fork of the inspect shell. Every feature');
  console.warn('    added to the shared viewer is a feature this module does not have.');
  console.warn('');
  return true;
}

function main() {
  if (!existsSync(MANIFEST)) {
    if (unmigrated(`no vendored viewer at ${relative(ROOT, SHARED)}`)) process.exit(0);
    console.error(`missing ${relative(ROOT, MANIFEST)}`);
    console.error('Run: node ../digital-3d-shared-contracts/tools/sync_viewer_ui.mjs --to .');
    process.exit(1);
  }

  const expected = new Map();
  for (const line of readFileSync(MANIFEST, 'utf8').split('\n')) {
    if (!line.trim() || line.startsWith('#')) continue;
    const [hash, path] = line.split(/\s{2,}/);
    expected.set(path.trim(), hash.trim());
  }

  const present = new Set(walk(SHARED).filter((p) => p !== 'VIEWER-UI.sha256'));
  const drifted = [];
  const missing = [];
  const extra = [];

  for (const [path, hash] of expected) {
    const full = join(SHARED, path.split('/').join(process.platform === 'win32' ? '\\' : '/'));
    if (!existsSync(full)) {
      missing.push(path);
      continue;
    }
    if (sha256(canonical(readFileSync(full))) !== hash) drifted.push(path);
  }
  for (const path of present) if (!expected.has(path)) extra.push(path);

  if (drifted.length === 0 && missing.length === 0 && extra.length === 0) {
    console.log(`shared viewer in sync: ${expected.size} files match VIEWER-UI.sha256`);
    process.exit(0);
  }

  console.error('');
  console.error('  ! SHARED VIEWER HAS DRIFTED');
  for (const p of drifted) console.error(`    edited locally   viewer/shared/${p}`);
  for (const p of missing) console.error(`    deleted locally  viewer/shared/${p}`);
  for (const p of extra) console.error(`    not shared       viewer/shared/${p}`);
  console.error('');
  console.error('  viewer/shared/ is owned by digital-3d-shared-contracts and must not be edited');
  console.error('  here. Three bridge repositories once forked this code and only 2 of 23 files');
  console.error('  still matched. Make the change in the shared repository, then re-sync:');
  console.error('');
  console.error('    node ../digital-3d-shared-contracts/tools/sync_viewer_ui.mjs --to .');
  console.error('');
  process.exit(1);
}

main();
