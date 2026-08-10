import { useState } from 'react';

interface Reference {
  label: string;
  url: string;
  note: string;
  restricted?: boolean;
}

/**
 * Outbound photographic and documentary references.
 *
 * Deliberately links rather than embeds. The most thorough photographic documentation of this
 * bridge, HistoricBridges.org, grants publication only by written Letter of Agreement for
 * "one-time, one edition use only" with all rights reserved -- terms an open repository cannot
 * satisfy, because anyone may fork it. Linking is not reproduction, so a link is what this offers.
 *
 * See CONFIDENCE-MODEL.md section 6.5. Assets that MAY be shown are recorded in
 * sources/asset-manifest.json with display_permitted true; this panel is for the ones that may not.
 */
const REFERENCES: Reference[] = [
  {
    label: 'HistoricBridges.org — Manhattan Bridge photo gallery',
    url: 'https://historicbridges.org/bridges/browser/photosviewer.php?bridgebrowser=newyork/manhattan/&gallerynum=2&gallerysize=2',
    note: 'The most thorough modern detail photography of this bridge. All rights reserved; opens on their site because these images may not be copied here.',
    restricted: true,
  },
  {
    label: 'National Bridge Inventory data sheet — structure 36-2240027',
    url: 'https://historicbridges.org/newyork/manhattan/nbisheet.pdf',
    note: 'Federal inventory data, 2010, inspected November 2008. Public domain. Independently corroborates the main span and the navigation clearance; registered as SRC-024.',
  },
  {
    label: 'HAER survey NY-164 (item ny0980), Library of Congress',
    url: 'https://www.loc.gov/pictures/item/ny0980/',
    note: 'Eleven photographs and no measured drawings — the gap that leaves this model dependent on period text. See OQ-022 on the NY-127 caption discrepancy.',
  },
];

export default function ReferencePanel() {
  const [open, setOpen] = useState(false);

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
            {REFERENCES.map((ref) => (
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
