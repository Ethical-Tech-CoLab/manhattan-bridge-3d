import type { ControlEntry, PartMetadata, PartsDocument, UnitMode } from '../model';
import { CONFIDENCE_LABELS, MATERIAL_APPEARANCE, PROVENANCE_STYLE, formatLength } from '../model';

interface MetadataPanelProps {
  doc: PartsDocument;
  part: PartMetadata | null;
  unitMode: UnitMode;
}

function ControlChip({ control }: { control: ControlEntry }) {
  const title = `${control.key} = ${control.value} ${control.unit}` +
    (control.source_ids.length ? ` · ${control.source_ids.join(', ')}` : ' · no source (placeholder)') +
    `\n${control.notes}`;
  return (
    <span className={`chip chip-${control.confidence}`} title={title}>
      {control.control_id}
    </span>
  );
}

export default function MetadataPanel({ doc, part, unitMode }: MetadataPanelProps) {
  if (!part) {
    return (
      <div className="panel empty">
        <h2>Part metadata</h2>
        <p>Select a part in the model or in the component tree.</p>
        <dl>
          <dt>Model</dt>
          <dd>{doc.model} · milestone {doc.milestone}</dd>
          <dt>Built by</dt>
          <dd>{doc.generated_by}</dd>
          <dt>Built at</dt>
          <dd>{doc.generated_at}</dd>
          <dt>Control document</dt>
          <dd>
            {doc.control_document.path}
            <br />
            <code>{doc.control_document.sha256.slice(0, 16)}</code>
          </dd>
        </dl>
      </div>
    );
  }

  const controlsById = new Map(doc.controls.map((control) => [control.control_id, control]));
  const size = part.bbox_prototype_m.size;

  return (
    <div className="panel">
      <h2>{part.part_id}</h2>
      <div className={`confidence-banner conf-${part.confidence}`}>
        {CONFIDENCE_LABELS[part.confidence]}
      </div>
      <dl>
        <dt>System</dt>
        <dd>
          {part.system}
          {part.subsystem ? ` / ${part.subsystem}` : ''}
        </dd>
        <dt>Source basis</dt>
        <dd>{part.source_basis.join(', ')}</dd>
        <dt>Geometry provenance</dt>
        <dd>
          <span className="material-line">
            <span
              className="provenance-key"
              style={{
                borderColor: PROVENANCE_STYLE[part.geometry_provenance]?.color,
                borderStyle: PROVENANCE_STYLE[part.geometry_provenance]?.dash
                  ? (PROVENANCE_STYLE[part.geometry_provenance].dash![0] < 2 ? 'dotted' : 'dashed')
                  : 'solid',
              }}
            />
            <span>{PROVENANCE_STYLE[part.geometry_provenance]?.label ?? part.geometry_provenance}</span>
          </span>
          <span className="hint">{PROVENANCE_STYLE[part.geometry_provenance]?.description}</span>
        </dd>
        <dt>Material</dt>
        <dd>
          <span className="material-line">
            <span
              className="material-swatch"
              style={{ background: MATERIAL_APPEARANCE[part.material]?.color ?? '#666' }}
            />
            <span>
              {MATERIAL_APPEARANCE[part.material]?.label ?? part.material} · grade{' '}
              {part.material_confidence} · {part.material_id}
            </span>
          </span>
          <span className="hint">
            {part.material_sources.length > 0
              ? `from ${part.material_sources.join(', ')}`
              : 'no registered source names this material — placeholder'}
          </span>
        </dd>
        <dt>Units</dt>
        <dd>
          prototype {part.prototype_units} · HO {part.ho_scale_units}
        </dd>
        <dt>Scale</dt>
        <dd>{part.scale}</dd>
        <dt>Extent (X · Y · Z)</dt>
        <dd className="mono">
          {formatLength(size[0], unitMode, doc.ho_scale_denominator)}
          <br />
          {formatLength(size[1], unitMode, doc.ho_scale_denominator)}
          <br />
          {formatLength(size[2], unitMode, doc.ho_scale_denominator)}
        </dd>
        <dt>Geometry</dt>
        <dd>{part.geometry_kinds.join(', ')}</dd>
        <dt>Control references</dt>
        <dd className="chips">
          {part.control_refs.length === 0 ? (
            <em>none</em>
          ) : (
            part.control_refs.map((ref) => {
              const control = controlsById.get(ref);
              return control ? <ControlChip key={ref} control={control} /> : <span key={ref}>{ref}</span>;
            })
          )}
        </dd>
        {part.open_questions.length > 0 && (
          <>
            <dt>Open questions</dt>
            <dd className="chips">
              {part.open_questions.map((oq) => (
                <span key={oq} className="chip chip-D">
                  {oq}
                </span>
              ))}
            </dd>
          </>
        )}
        <dt>Notes</dt>
        <dd>{part.notes}</dd>
        <dt>Review</dt>
        <dd>
          {part.review_status} · {part.last_modified_by_agent}
        </dd>
      </dl>
    </div>
  );
}
