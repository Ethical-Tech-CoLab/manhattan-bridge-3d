import type { Confidence, PartMetadata, PartsDocument } from '../src/model';
import { CONFIDENCE_LABELS } from '../src/model';

interface PartTreeProps {
  doc: PartsDocument;
  selectedId: string | null;
  hiddenSystems: Set<string>;
  hiddenParts: Set<string>;
  onSelect: (partId: string) => void;
  onToggleSystem: (system: string) => void;
  onTogglePart: (partId: string) => void;
}

function Badge({ confidence }: { confidence: Confidence }) {
  return (
    <span className={`badge badge-${confidence}`} title={CONFIDENCE_LABELS[confidence]}>
      {confidence}
    </span>
  );
}

function PartRow({
  part,
  selected,
  hidden,
  onSelect,
  onToggle,
}: {
  part: PartMetadata;
  selected: boolean;
  hidden: boolean;
  onSelect: () => void;
  onToggle: () => void;
}) {
  return (
    <li className={`part-row${selected ? ' selected' : ''}${hidden ? ' hidden' : ''}`}>
      <input type="checkbox" checked={!hidden} onChange={onToggle} aria-label={`show ${part.part_id}`} />
      <button type="button" onClick={onSelect} title={part.notes}>
        <Badge confidence={part.confidence} />
        <span className="part-name">{part.part_id}</span>
      </button>
    </li>
  );
}

export default function PartTree(props: PartTreeProps) {
  const { doc, selectedId, hiddenSystems, hiddenParts, onSelect, onToggleSystem, onTogglePart } = props;
  const byId = new Map(doc.parts.map((part) => [part.part_id, part]));

  return (
    <div className="tree">
      {Object.entries(doc.taxonomy).map(([system, node]) => {
        const systemHidden = hiddenSystems.has(system);
        const count =
          node.parts.length +
          Object.values(node.subsystems).reduce((total, ids) => total + ids.length, 0);
        return (
          <section key={system} className={`system${systemHidden ? ' hidden' : ''}`}>
            <header>
              <input
                type="checkbox"
                checked={!systemHidden}
                onChange={() => onToggleSystem(system)}
                aria-label={`show ${system}`}
              />
              <h3>{system.replace(/_/g, ' ')}</h3>
              <span className="count">{count}</span>
            </header>
            {node.parts.length > 0 && (
              <ul>
                {node.parts.map((id) => {
                  const part = byId.get(id);
                  if (!part) return null;
                  return (
                    <PartRow
                      key={id}
                      part={part}
                      selected={id === selectedId}
                      hidden={hiddenParts.has(id)}
                      onSelect={() => onSelect(id)}
                      onToggle={() => onTogglePart(id)}
                    />
                  );
                })}
              </ul>
            )}
            {Object.entries(node.subsystems).map(([subsystem, ids]) => (
              <div key={subsystem} className="subsystem">
                <h4>{subsystem.replace(/_/g, ' ')}</h4>
                <ul>
                  {ids.map((id) => {
                    const part = byId.get(id);
                    if (!part) return null;
                    return (
                      <PartRow
                        key={id}
                        part={part}
                        selected={id === selectedId}
                        hidden={hiddenParts.has(id)}
                        onSelect={() => onSelect(id)}
                        onToggle={() => onTogglePart(id)}
                      />
                    );
                  })}
                </ul>
              </div>
            ))}
          </section>
        );
      })}
    </div>
  );
}
