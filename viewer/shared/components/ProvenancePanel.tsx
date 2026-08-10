import type { GeometryProvenance, PartsDocument } from '../model';
import { PROVENANCE_ORDER, PROVENANCE_STYLE } from '../model';

interface ProvenancePanelProps {
  doc: PartsDocument;
  outlines: boolean;
  onToggleOutlines: () => void;
  hidden: Set<string>;
  onToggleProvenance: (state: GeometryProvenance) => void;
}

/**
 * Geometry provenance, adopted from SRC-018 (manhattan-bridge-noise-dumbo,
 * VISUAL-MODEL-FRAMEWORK.md sections 5.4 and 5.5).
 *
 * Three requirements from that framework are implemented here rather than described:
 * a standing tally that is always on screen, a filter that hides rather than fades, and a
 * statement of what each state means. The fourth, locus on selection, lives in the metadata panel.
 */
export default function ProvenancePanel({
  doc,
  outlines,
  onToggleOutlines,
  hidden,
  onToggleProvenance,
}: ProvenancePanelProps) {
  const tally = (doc.measures.geometry_provenance_tally ?? {}) as Record<string, number>;
  const total = PROVENANCE_ORDER.reduce((sum, state) => sum + (tally[state] ?? 0), 0);

  return (
    <section className="provenance-panel">
      <header>
        <h3>Geometry provenance</h3>
        <label className="provenance-outline-toggle">
          <input type="checkbox" checked={outlines} onChange={onToggleOutlines} />
          <span>outlines</span>
        </label>
      </header>

      <p className="provenance-intro">
        How the <em>shape and position</em> of each part are known — a separate question from how
        thoroughly its sources were read. Switch a state off to hide that geometry entirely.
      </p>

      <ul className="provenance-list">
        {PROVENANCE_ORDER.map((state) => {
          const style = PROVENANCE_STYLE[state];
          const count = tally[state] ?? 0;
          const isHidden = hidden.has(state);
          return (
            <li key={state} className={isHidden ? 'is-hidden' : undefined}>
              <label>
                <input
                  type="checkbox"
                  checked={!isHidden}
                  onChange={() => onToggleProvenance(state)}
                  disabled={count === 0}
                />
                <span
                  className="provenance-key"
                  style={{
                    borderColor: style.color,
                    borderStyle: style.dash ? (style.dash[0] < 2 ? 'dotted' : 'dashed') : 'solid',
                  }}
                />
                <span className="provenance-label">{style.label}</span>
                <span className="provenance-count">{count}</span>
              </label>
              <p>{style.description}</p>
            </li>
          );
        })}
      </ul>

      <p className="provenance-rule">
        {(tally.MEASURED ?? 0) === 0 && (tally.DOCUMENTED ?? 0) === 0
          ? `Nothing in this model is measured or documented. All ${total} parts are reasoned or judged.`
          : `${tally.DOCUMENTED ?? 0} of ${total} parts rest on a source that states this element's own dimension. None is measured.`}
      </p>
      <p className="provenance-rule">
        No dimension is annotated on assumed geometry: if we do not know where it is, we do not get
        to say how big it is.
      </p>
    </section>
  );
}
