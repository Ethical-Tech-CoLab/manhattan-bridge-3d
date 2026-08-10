import { useState } from 'react';
import type { Reference } from '../model';

interface ReferencePanelProps {
  references: Reference[];
}

/**
 * Outbound photographic and documentary references.
 *
 * Deliberately links rather than embeds. Some of the best documentation of these bridges is
 * all-rights-reserved -- HistoricBridges.org grants publication only by written Letter of Agreement
 * for "one-time, one edition use only", terms no forkable open repository can satisfy. Linking is
 * not reproduction, so a link is what this offers.
 *
 * The list is a prop, not a constant, because this component is shared by every bridge. Each module
 * supplies its own references through model.config.json; nothing here names a bridge.
 *
 * See CONFIDENCE-MODEL.md section 6.5.
 */
export default function ReferencePanel({ references }: ReferencePanelProps) {
  const [open, setOpen] = useState(false);
  if (references.length === 0) return null;

  return (
    <section className="reference-panel">
      <button type="button" className="reference-toggle" onClick={() => setOpen((v) => !v)}>
        <span>Photographic references</span>
        <span>{open ? '−' : '+'}</span>
      </button>

      {open && (
        <div className="reference-body">
          <p className="reference-intro">
            External sources consulted while modelling. Linked, not copied — see{' '}
            <code>CONFIDENCE-MODEL.md</code> section 6.5.
          </p>
          <ul>
            {references.map((ref) => (
              <li key={ref.url}>
                <a href={ref.url} target="_blank" rel="noreferrer noopener">
                  {ref.label}
                </a>
                {ref.restricted && <span className="reference-flag">all rights reserved</span>}
                <p>{ref.note}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
