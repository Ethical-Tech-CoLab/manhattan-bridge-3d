import type { ViewMode } from '../model';
import { VIEW_ORDER, VIEW_PRESETS, niceScaleLength } from '../model';

interface ViewBarProps {
  mode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
  metresPerPixel: number;
  unitMode: 'prototype' | 'ho';
  scaleDenominator: number;
}

function formatBar(metres: number, unitMode: 'prototype' | 'ho', denominator: number): string {
  if (unitMode === 'ho') {
    const mm = (metres / denominator) * 1000;
    return mm >= 1000 ? `${(mm / 1000).toFixed(2)} m` : `${mm.toFixed(mm < 10 ? 1 : 0)} mm`;
  }
  const feet = metres / 0.3048;
  return metres >= 1
    ? `${metres >= 10 ? metres.toFixed(0) : metres.toFixed(1)} m  ·  ${feet.toFixed(0)} ft`
    : `${(metres * 100).toFixed(0)} cm  ·  ${(feet * 12).toFixed(0)} in`;
}

/**
 * View selector plus a scale bar.
 *
 * The scale bar exists so a screenshot carries its own scale. Without one, an image of this model
 * cannot be read outside the app, which is the difference between a model you can look at and one
 * you can publish. It is only exact in the orthographic modes; in `iso` the projection foreshortens
 * with depth, so it is labelled as approximate rather than quietly implying precision it lacks.
 */
export default function ViewBar({
  mode,
  onModeChange,
  metresPerPixel,
  unitMode,
  scaleDenominator,
}: ViewBarProps) {
  const barMetres = niceScaleLength(metresPerPixel);
  const barPx = Math.round(barMetres / metresPerPixel);
  const exact = VIEW_PRESETS[mode].orthographic;

  return (
    <div className="view-bar">
      <div className="view-modes" role="group" aria-label="view">
        {VIEW_ORDER.map((key) => (
          <button
            key={key}
            type="button"
            className={key === mode ? 'active' : undefined}
            onClick={() => onModeChange(key)}
            title={VIEW_PRESETS[key].description}
          >
            {VIEW_PRESETS[key].label}
          </button>
        ))}
      </div>

      {Number.isFinite(barPx) && barPx > 0 && (
        <div className="scale-bar" title={exact ? 'Parallel projection: this scale is exact anywhere in the frame.' : 'Perspective projection: this scale is only true at the orbit target depth.'}>
          <div className="scale-bar-rule" style={{ width: `${Math.min(barPx, 320)}px` }} />
          <span>
            {formatBar(barMetres, unitMode, scaleDenominator)}
            {exact ? '' : ' (approx)'}
          </span>
        </div>
      )}
    </div>
  );
}
