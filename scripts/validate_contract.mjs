/**
 * Validate every published contract document in this module against the shared schemas.
 *
 * `digital-3d-shared-contracts/tools/validate.mjs` validates whole documents. The bridge publishes
 * 81 metadata records inside one envelope, so this walks the envelope and validates each record
 * individually. It also re-checks the manifest, ladder, registry and frame, so one command covers
 * the whole contract surface.
 *
 *   node scripts/validate_contract.mjs
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, '..');
const CONTRACTS = resolve('c:/Dev/digital-3d-shared-contracts');
const PUBLIC = join(REPO, 'viewer', 'public');

const require = createRequire(join(CONTRACTS, 'package.json'));
const Ajv = require('ajv/dist/2020.js');
const addFormats = require('ajv-formats');

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

const schemaDir = join(CONTRACTS, 'schemas');
for (const file of readdirSync(schemaDir).filter((f) => f.endsWith('.json'))) {
  ajv.addSchema(JSON.parse(readFileSync(join(schemaDir, file), 'utf8')));
}
const validator = (name) =>
  ajv.getSchema(`https://contracts.digital-3d.org/v1/${name}.schema.json`);

const read = (p) => JSON.parse(readFileSync(p, 'utf8'));
let failures = 0;

function check(label, schemaName, doc) {
  const validate = validator(schemaName);
  if (!validate(doc)) {
    failures += 1;
    console.log(`  FAIL ${label}  [${schemaName}]`);
    for (const e of validate.errors.slice(0, 6)) {
      console.log(`       ${e.instancePath || '/'} ${e.message}`);
    }
  } else {
    console.log(`  ok   ${label}  [${schemaName}]`);
  }
}

console.log('validating published contract surface\n');

check('bridge-manifest.json', 'module-manifest', read(join(PUBLIC, 'bridge-manifest.json')));
check('bridge/lod.json', 'lod', read(join(PUBLIC, 'bridge', 'lod.json')));
check('bridge/asset-registry.json', 'asset-registry', read(join(PUBLIC, 'bridge', 'asset-registry.json')));
check('frames/nyc-harbor-enu.json', 'georeference', read(join(PUBLIC, 'frames', 'nyc-harbor-enu.json')));

// Every metadata record, individually.
const metadata = read(join(PUBLIC, 'bridge', 'metadata.json'));
const validateMeta = validator('metadata');
let bad = 0;
for (const record of metadata.records) {
  if (!validateMeta(record)) {
    bad += 1;
    if (bad <= 3) {
      console.log(`  FAIL metadata record ${record.local_id ?? '?'}`);
      for (const e of validateMeta.errors.slice(0, 4)) {
        console.log(`       ${e.instancePath || '/'} ${e.message}`);
      }
    }
  }
}
if (bad) {
  failures += 1;
  console.log(`  FAIL bridge/metadata.json  [metadata]  ${bad}/${metadata.records.length} records invalid`);
} else {
  console.log(`  ok   bridge/metadata.json  [metadata]  ${metadata.records.length} records`);
}

// Cross-document invariants the schemas cannot express on their own.
const manifest = read(join(PUBLIC, 'bridge-manifest.json'));
const registry = read(join(PUBLIC, 'bridge', 'asset-registry.json'));
const ids = new Set(registry.assets.map((a) => a.asset_id));

const invariants = [
  ['proxy asset_id is registered', ids.has(manifest.proxy.asset_id)],
  [
    'every handoff focus_asset is registered',
    manifest.handoff.entry_points.every((e) => !e.focus_asset || ids.has(e.focus_asset)),
  ],
  ['placement scale is 1 for georeferenced delivery', manifest.placement.scale === 1],
  ['placement frame matches the registry frame', manifest.placement.frame === registry.frame_id],
  [
    'proxy max_level exists on the ladder',
    read(join(PUBLIC, 'bridge', 'lod.json')).levels.some((l) => l.level === manifest.proxy.max_level),
  ],
  [
    'metadata asset_ids all appear in the registry',
    metadata.records.every((r) => ids.has(r.asset_id)),
  ],
];

console.log('\ncross-document invariants');
for (const [label, ok] of invariants) {
  console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${label}`);
  if (!ok) failures += 1;
}

console.log(failures ? `\n${failures} check(s) failed` : '\nall documents valid');

/**
 * URL resolution, checked against BOTH deployment layouts.
 *
 * Mirrors the kernel's resolveUrl exactly: absolute or root-absolute passes through, otherwise the
 * filename is stripped from the base and the relative part concatenated. Getting this wrong is
 * silent and total — the manifest loads and every payload 404s — so it is worth asserting rather
 * than eyeballing.
 */
function resolveUrl(base, relative) {
  if (/^([a-z]+:)?\/\//i.test(relative) || relative.startsWith('/')) return relative;
  return base.replace(/[^/]*$/, '') + relative;
}
const normalise = (p) => new URL(p, 'https://example.org').pathname;

console.log('\nURL resolution');
const layouts = [
  ['served at own root      ', '/bridge-manifest.json'],
  ['co-served under district', '/modules/manhattan-bridge/bridge-manifest.json'],
];
let urlFailures = 0;
for (const [label, manifestUrl] of layouts) {
  const prefix = manifestUrl.replace(/bridge-manifest\.json$/, '');
  const frameUrl = normalise(resolveUrl(manifestUrl, manifest.georeference.url));
  const registryUrl = normalise(resolveUrl(manifestUrl, manifest.asset_registry_url));
  const ladderUrl = normalise(resolveUrl(manifestUrl, manifest.lod_ladder.url));
  const base = normalise(resolveUrl(registryUrl, registry.base_url));
  const proxyAsset = registry.assets.find((a) => a.asset_id === manifest.proxy.asset_id);
  const glbUrl = normalise(resolveUrl(base, proxyAsset.variants[0].url));
  const metaUrl = normalise(resolveUrl(base, 'bridge/metadata.json'));

  const expect = {
    frame: `${prefix}frames/nyc-harbor-enu.json`,
    ladder: `${prefix}bridge/lod.json`,
    registry: `${prefix}bridge/asset-registry.json`,
    glb: `${prefix}assets/bridge.lod2.glb`,
    metadata: `${prefix}bridge/metadata.json`,
  };
  const got = { frame: frameUrl, ladder: ladderUrl, registry: registryUrl, glb: glbUrl, metadata: metaUrl };
  const ok = Object.keys(expect).every((k) => expect[k] === got[k]);
  console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${label}  ->  ${got.glb}`);
  if (!ok) {
    urlFailures += 1;
    for (const k of Object.keys(expect)) {
      if (expect[k] !== got[k]) console.log(`       ${k}: got ${got[k]} want ${expect[k]}`);
    }
  }
}

const total = failures + urlFailures;
console.log(total ? `\n${total} check(s) failed` : '\nall documents valid, both deployment layouts resolve');
process.exit(total ? 1 : 0);
