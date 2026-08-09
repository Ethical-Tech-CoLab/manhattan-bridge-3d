import type { PartsDocument, UnitMode } from '../src/model';
import { formatLength } from '../src/model';

interface DimensionPanelProps {
  doc: PartsDocument;
  unitMode: UnitMode;
}

/**
 * Measurement overlay. The scene is never rescaled: the HO toggle only switches the readout,
 * per SCALE-HO.md section 3.
 */
export default function DimensionPanel({ doc, unitMode }: DimensionPanelProps) {
  const linear = doc.controls.filter((control) => control.ho !== null && !control.is_placeholder);
  const placeholders = doc.controls.filter((control) => control.is_placeholder);

  return (
    <div className="panel">
      <h2>Control dimensions</h2>
      <p className="footnote">
        {unitMode === 'ho' ? `Reported at ${doc.ho_scale_denominator} : 1 reduction (HO).` : 'Reported at prototype scale.'}{' '}
        Values come from {doc.control_document.path}.
      </p>
      <table className="dims">
        <thead>
          <tr>
            <th>Control</th>
            <th>Dimension</th>
            <th>{unitMode === 'ho' ? 'HO' : 'Prototype'}</th>
          </tr>
        </thead>
        <tbody>
          {linear.map((control) => (
            <tr key={control.control_id} title={control.notes}>
              <td>
                <span className={`chip chip-${control.confidence}`}>{control.control_id}</span>
              </td>
              <td>{control.key.replace(/_/g, ' ')}</td>
              <td className="mono">{formatLength(control.value_m, unitMode, doc.ho_scale_denominator)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Reference stations</h3>
      <table className="dims">
        <tbody>
          {doc.stations.map((station) => (
            <tr key={station.station_id} title={station.notes}>
              <td>
                <span className={`chip chip-${station.confidence}`}>{station.station_id}</span>
              </td>
              <td>{station.name}</td>
              <td className="mono">{formatLength(station.x_m, unitMode, doc.ho_scale_denominator)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Placeholders in force ({placeholders.length})</h3>
      <p className="footnote">
        These are shape hints, not measurements. They are never citable as dimensions and are the
        reason most parts are graded D.
      </p>
      <ul className="placeholder-list">
        {placeholders.map((control) => (
          <li key={control.control_id} title={control.notes}>
            <span className="chip chip-D">{control.control_id}</span> {control.key.replace(/_/g, ' ')}
            <span className="mono"> {control.value} {control.unit}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
