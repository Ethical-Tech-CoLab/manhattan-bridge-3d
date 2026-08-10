import type { UnitMode, ViewerConfig } from '../model';

interface ToolbarProps {
  config: ViewerConfig;
  unitMode: UnitMode;
  onUnitModeChange: (mode: UnitMode) => void;
  onResetView: () => void;
  onShowAll: () => void;
  panel: 'metadata' | 'dimensions';
  onPanelChange: (panel: 'metadata' | 'dimensions') => void;
}

export default function Toolbar({
  config,
  unitMode,
  onUnitModeChange,
  onResetView,
  onShowAll,
  panel,
  onPanelChange,
}: ToolbarProps) {
  return (
    <header className="toolbar">
      <div className="title">
        <h1>{config.title}</h1>
        <p>{config.subtitle}</p>
      </div>
      <div className="controls">
        <div className="segmented" role="group" aria-label="unit mode">
          <button
            type="button"
            className={unitMode === 'prototype' ? 'active' : ''}
            onClick={() => onUnitModeChange('prototype')}
          >
            Prototype
          </button>
          <button
            type="button"
            className={unitMode === 'ho' ? 'active' : ''}
            onClick={() => onUnitModeChange('ho')}
          >
            {config.scaleLabel}
          </button>
        </div>
        <div className="segmented" role="group" aria-label="side panel">
          <button
            type="button"
            className={panel === 'metadata' ? 'active' : ''}
            onClick={() => onPanelChange('metadata')}
          >
            Metadata
          </button>
          <button
            type="button"
            className={panel === 'dimensions' ? 'active' : ''}
            onClick={() => onPanelChange('dimensions')}
          >
            Dimensions
          </button>
        </div>
        <button type="button" onClick={onShowAll}>
          Show all
        </button>
        <button type="button" onClick={onResetView}>
          Reset view
        </button>
      </div>
    </header>
  );
}
