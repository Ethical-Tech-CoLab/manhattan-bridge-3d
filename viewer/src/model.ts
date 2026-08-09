/**
 * Types and helpers for the part metadata manifest produced by
 * scripts/build_control_skeleton.py.
 *
 * The viewer is model-agnostic: it only assumes a GLB whose part nodes carry the metadata contract
 * from CONFIDENCE-MODEL.md in their glTF `extras`, plus a matching parts.json manifest.
 */

export type Confidence = 'A' | 'B' | 'C' | 'D';

export interface PartMetadata {
  part_id: string;
  system: string;
  subsystem: string | null;
  source_basis: string[];
  confidence: Confidence;
  prototype_units: string;
  ho_scale_units: string;
  notes: string;
  scale: string;
  last_modified_by_agent: string;
  review_status: string;
  control_refs: string[];
  open_questions: string[];
  basis_confidence: Confidence;
  material: MaterialName;
  material_id: string;
  material_confidence: Confidence;
  material_sources: string[];
  geometry_kinds: string[];
  bbox_prototype_m: { min: number[]; max: number[]; size: number[] };
  bbox_ho_mm: { size: number[] };
}

/** Closed vocabulary, mirroring ALLOWED_MATERIALS in scripts/control_model.py. */
export type MaterialName =
  | 'masonry'
  | 'concrete'
  | 'steel_structural'
  | 'steel_wire'
  | 'roadway_surface'
  | 'reference';

export interface MaterialAppearance {
  label: string;
  color: string;
  roughness: number;
  metalness: number;
  /** Opacity used in material mode. Schematic transparency is abandoned so the bridge reads solid. */
  opacity: number;
}

/**
 * How each controlled material is rendered.
 *
 * These are appearance values, not claims about the bridge: the *assignment* of a material to a
 * part is controlled and graded in GEOMETRY-CONTROL.md section 7, and this table only says what
 * masonry looks like. Keeping the two apart is why a grade-D material assignment can still be
 * rendered convincingly without the render implying the assignment is certain -- the material
 * grade is shown in the metadata panel and by the provenance outline.
 */
export const MATERIAL_APPEARANCE: Record<MaterialName, MaterialAppearance> = {
  masonry: { label: 'masonry', color: '#9a8f7d', roughness: 0.96, metalness: 0.02, opacity: 1 },
  concrete: { label: 'concrete', color: '#8d8d88', roughness: 0.92, metalness: 0.0, opacity: 1 },
  steel_structural: { label: 'structural steel', color: '#7d8894', roughness: 0.52, metalness: 0.82, opacity: 1 },
  steel_wire: { label: 'wire rope', color: '#8a8577', roughness: 0.38, metalness: 0.9, opacity: 1 },
  roadway_surface: { label: 'roadway surface', color: '#4a4a4d', roughness: 0.98, metalness: 0.0, opacity: 1 },
  reference: { label: 'reference geometry', color: '#5f6b78', roughness: 1, metalness: 0, opacity: 0.25 },
};

export interface ControlEntry {
  control_id: string;
  key: string;
  value: number;
  unit: string;
  value_m: number;
  source_ids: string[];
  confidence: Confidence;
  is_placeholder: boolean;
  notes: string;
  ho: HoReport | null;
}

export interface HoReport {
  prototype_m: number;
  prototype_ft: number;
  prototype_in: number;
  ho_mm: number;
  ho_in: number;
  ho_ft: number;
}

export interface Station {
  station_id: string;
  name: string;
  x_m: number;
  confidence: Confidence;
  control_refs: string[];
  notes: string;
  ho: HoReport;
}

export interface PartsDocument {
  schema_version: string;
  model: string;
  milestone: number;
  generated_by: string;
  generated_at: string;
  control_document: { path: string; sha256: string };
  ho_scale_denominator: number;
  coordinate_system: Record<string, string>;
  confidence_colors: Record<Confidence, string>;
  taxonomy: Record<string, { parts: string[]; subsystems: Record<string, string[]> }>;
  stations: Station[];
  elevations: Array<{ elevation_id: string; name: string; z_m: number; confidence: Confidence; notes: string }>;
  controls: ControlEntry[];
  measures: Record<string, unknown>;
  parts: PartMetadata[];
}

export interface ViewerConfig {
  title: string;
  subtitle: string;
  modelUrl: string;
  metadataUrl: string;
  scaleDenominator: number;
  scaleLabel: string;
  background: string;
  lineRaycastThreshold: number;
  camera: { position: [number, number, number]; target: [number, number, number]; near: number; far: number; fov: number };
  /** Multiplier applied to the auto-framed camera distance. Defaults to 1.2. */
  framePadding?: number;
  governance: Record<string, string>;
  notImplementedYet: string[];
}

export const CONFIDENCE_LABELS: Record<Confidence, string> = {
  A: 'A · official dimension or archival drawing',
  B: 'B · consistent photos plus control geometry',
  C: 'C · aligned mesh or photogrammetry',
  D: 'D · inferred, decorative, or placeholder',
};

export type UnitMode = 'prototype' | 'ho';

/** Format a prototype length in meters for display in the active unit mode. */
export function formatLength(meters: number, mode: UnitMode, scaleDenominator: number): string {
  if (mode === 'ho') {
    const mm = (meters / scaleDenominator) * 1000;
    const inches = mm / 25.4;
    return `${mm.toFixed(Math.abs(mm) < 10 ? 2 : 1)} mm  /  ${inches.toFixed(Math.abs(inches) < 1 ? 3 : 2)} in`;
  }
  const feet = meters / 0.3048;
  return `${meters.toFixed(3)} m  /  ${feet.toFixed(2)} ft`;
}

export function partLabel(part: PartMetadata): string {
  return part.part_id.replace(/_/g, ' ');
}
