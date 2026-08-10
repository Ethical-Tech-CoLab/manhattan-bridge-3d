import type { Confidence, PartsDocument } from '../model';
import { CONFIDENCE_LABELS } from '../model';

interface ConfidenceLegendProps {
  doc: PartsDocument;
  active: boolean;
  onToggle: () => void;
}

const GRADES: Confidence[] = ['A', 'B', 'C', 'D'];

export default function ConfidenceLegend({ doc, active, onToggle }: ConfidenceLegendProps) {
  const counts = GRADES.reduce<Record<Confidence, number>>(
    (acc, grade) => {
      acc[grade] = doc.parts.filter((part) => part.confidence === grade).length;
      return acc;
    },
    { A: 0, B: 0, C: 0, D: 0 },
  );

  return (
    <div className="legend">
      <header>
        <h3>Source confidence</h3>
        <label className="switch">
          <input type="checkbox" checked={active} onChange={onToggle} />
          <span>overlay</span>
        </label>
      </header>
      <ul>
        {GRADES.map((grade) => (
          <li key={grade} title={CONFIDENCE_LABELS[grade]}>
            <span className="swatch" style={{ background: doc.confidence_colors[grade] }} />
            <span className="grade">{grade}</span>
            <span className="legend-label">{CONFIDENCE_LABELS[grade].split('· ')[1]}</span>
            <span className="count">{counts[grade]}</span>
          </li>
        ))}
      </ul>
      <p className="footnote">
        Grades follow CONFIDENCE-MODEL.md. A part is graded no better than the weakest control value
        it consumes, so every placeholder plan dimension pulls its part down to D.
      </p>
    </div>
  );
}
