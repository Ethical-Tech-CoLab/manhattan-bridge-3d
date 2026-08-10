import type { CompareMode, Nudge, ReferenceView, ReferenceViewsDocument } from '../model';

interface Props {
  doc: ReferenceViewsDocument;
  activeId: string | null;
  mode: CompareMode;
  nudge: Nudge;
  onPick: (view: ReferenceView | null) => void;
  onMode: (mode: CompareMode) => void;
  onNudge: (n: Partial<Nudge>) => void;
  onRecall: () => void;
  onReset: () => void;
}

const MODES: { id: CompareMode; label: string; hint: string }[] = [
  { id: 'off', label: 'Off', hint: 'model only' },
  { id: 'overlay', label: 'Overlay', hint: 'reference over the model, adjustable' },
  { id: 'split', label: 'Side by side', hint: 'drag the divider' },
];

/**
 * Compare against the record. Driven entirely by reference-views.json, so the same panel works for
 * any module that ships one.
 */
export default function ComparePanel(props: Props) {
  const { doc, activeId, mode, nudge } = props;
  const active = doc.views.find((v) => v.id === activeId) ?? null;
  const drawings = doc.views.filter((v) => v.kind === 'drawing');
  const photographs = doc.views.filter((v) => v.kind === 'photograph');

  const group = (label: string, views: ReferenceView[]) =>
    views.length === 0 ? null : (
      <div className="cmp-group" key={label}>
        <h3>{label}</h3>
        <ul className="cmp-list">
          {views.map((v) => (
            <li key={v.id}>
              <button
                type="button"
                className={`cmp-item ${activeId === v.id ? 'selected' : ''}`}
                onClick={() => props.onPick(activeId === v.id ? null : v)}
              >
                <img src={v.image} alt="" loading="lazy" />
                <span className="cmp-item-text">
                  <b>{v.title}</b>
                  {v.subtitle && <em>{v.subtitle}</em>}
                  <span className="src">{v.source_id}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    );

  return (
    <section className="panel compare">
      <h2>Compare against the record</h2>
      <p className="hint">
        Pick a reference to fly the camera to its viewpoint, then overlay or split the frame. Every
        image here is a work of the U.S. Government with no known copyright restrictions.
      </p>

      <div className="cmp-modes" role="group" aria-label="compare mode">
        {MODES.map((m) => (
          <button
            key={m.id}
            type="button"
            title={m.hint}
            disabled={m.id !== 'off' && !active}
            className={mode === m.id ? 'on' : ''}
            onClick={() => props.onMode(m.id)}
          >
            {m.label}
          </button>
        ))}
      </div>

      {group('Measured drawings', drawings)}
      {group('Photographs', photographs)}

      {active && (
        <div className="cmp-active">
          <h3>Alignment</h3>
          <p className="hint warn">
            The camera pose is <strong>author-set and graded {active.pose_confidence}</strong>. No
            source says where the photographer stood. Nudge it freely — nothing in the model depends
            on it.
          </p>
          <label className="cmp-slider">
            opacity
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={nudge.opacity}
              onChange={(e) => props.onNudge({ opacity: Number(e.target.value) })}
            />
            <span>{Math.round(nudge.opacity * 100)}%</span>
          </label>
          <label className="cmp-slider">
            scale
            <input
              type="range"
              min={0.5}
              max={2}
              step={0.005}
              value={nudge.scale}
              onChange={(e) => props.onNudge({ scale: Number(e.target.value) })}
            />
            <span>{nudge.scale.toFixed(2)}×</span>
          </label>
          <label className="cmp-slider">
            x
            <input
              type="range"
              min={-50}
              max={50}
              step={0.5}
              value={nudge.dx}
              onChange={(e) => props.onNudge({ dx: Number(e.target.value) })}
            />
            <span>{nudge.dx.toFixed(0)}%</span>
          </label>
          <label className="cmp-slider">
            y
            <input
              type="range"
              min={-50}
              max={50}
              step={0.5}
              value={nudge.dy}
              onChange={(e) => props.onNudge({ dy: Number(e.target.value) })}
            />
            <span>{nudge.dy.toFixed(0)}%</span>
          </label>
          <div className="cmp-buttons">
            <button type="button" onClick={props.onRecall}>
              Recall pose
            </button>
            <button type="button" onClick={props.onReset}>
              Reset alignment
            </button>
          </div>

          {active.notes && <p className="note">{active.notes}</p>}
          <p className="credit">
            {active.credit} <em>{active.license}</em>
            {active.source_url && (
              <>
                {' '}
                <a href={active.source_url} target="_blank" rel="noreferrer">
                  source record
                </a>
              </>
            )}
          </p>
        </div>
      )}

      <p className="hint">{doc.pose_disclaimer}</p>

      {doc.links && doc.links.length > 0 && (
        <div className="cmp-group">
          <h3>Linked, not copied</h3>
          <p className="hint">
            Reference material this project may not redistribute. Opened in a new tab, never served
            from here.
          </p>
          <ul className="cmp-links">
            {doc.links.map((l) => (
              <li key={l.id}>
                <a href={l.url} target="_blank" rel="noreferrer">
                  {l.title}
                </a>
                <span className="src">
                  {l.publisher} · {l.source_id}
                </span>
                <span className="lic">{l.license}</span>
                {l.notes && <p className="note">{l.notes}</p>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
