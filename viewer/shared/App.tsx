import { useCallback, useEffect, useMemo, useState } from 'react';
import BridgeViewer from './BridgeViewer';
import ComparePanel from './components/ComparePanel';
import CompareStage from './components/CompareStage';
import ConfidenceLegend from './components/ConfidenceLegend';
import DimensionPanel from './components/DimensionPanel';
import MetadataPanel from './components/MetadataPanel';
import PartTree from './components/PartTree';
import { PhotoGallery, usePhotoManifest } from './components/PhotoGallery';
import ProvenancePanel from './components/ProvenancePanel';
import ReferencePanel from './components/ReferencePanel';
import Toolbar from './components/Toolbar';
import PresentationNotice from './components/PresentationNotice';
import ViewBar from './components/ViewBar';
import { NUDGE_IDENTITY } from './model';
import type {
  CompareMode,
  GeometryProvenance,
  Nudge,
  PartsDocument,
  ReferenceView,
  ReferenceViewsDocument,
  UnitMode,
  ViewMode,
  ViewerConfig,
} from './model';

export default function App() {
  const [config, setConfig] = useState<ViewerConfig | null>(null);
  const [doc, setDoc] = useState<PartsDocument | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hiddenSystems, setHiddenSystems] = useState<Set<string>>(new Set());
  const [hiddenParts, setHiddenParts] = useState<Set<string>>(new Set());
  const [confidenceOverlay, setConfidenceOverlay] = useState(false);
  const [materialMode, setMaterialMode] = useState(true);
  const [provenanceOutlines, setProvenanceOutlines] = useState(true);
  const [hiddenProvenance, setHiddenProvenance] = useState<Set<string>>(new Set());
  const [unitMode, setUnitMode] = useState<UnitMode>('prototype');
  const [panel, setPanel] = useState<'metadata' | 'dimensions'>('metadata');
  const [focusToken, setFocusToken] = useState(0);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  // Bumped on every layout change so the viewer can resize its drawing buffer deterministically,
  // rather than depending on the browser to report the CSS grid column change in time.
  const layoutToken = (leftCollapsed ? 1 : 0) + (rightCollapsed ? 2 : 0);
  const [viewMode, setViewMode] = useState<ViewMode>('iso');
  const [metresPerPixel, setMetresPerPixel] = useState(1);

  // Optional evidence features. Both stay null for a module that publishes neither, and the
  // corresponding panels are then never mounted.
  const [refs, setRefs] = useState<ReferenceViewsDocument | null>(null);
  const [activeRef, setActiveRef] = useState<ReferenceView | null>(null);
  const [compareMode, setCompareMode] = useState<CompareMode>('off');
  const [nudge, setNudge] = useState<Nudge>(NUDGE_IDENTITY);
  const [poseNonce, setPoseNonce] = useState(0);
  const [photoId, setPhotoId] = useState<string | null>(null);
  const photos = usePhotoManifest(config?.photoManifestUrl);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const configResponse = await fetch('model.config.json');
        if (!configResponse.ok) throw new Error(`model.config.json: ${configResponse.status}`);
        const loadedConfig: ViewerConfig = await configResponse.json();
        const metadataResponse = await fetch(loadedConfig.metadataUrl);
        if (!metadataResponse.ok) throw new Error(`${loadedConfig.metadataUrl}: ${metadataResponse.status}`);
        const loadedDoc: PartsDocument = await metadataResponse.json();
        if (cancelled) return;
        setConfig(loadedConfig);
        setDoc(loadedDoc);
        // Reference imagery is optional and must never block the model from loading: a module
        // that ships none simply has no compare panel.
        if (loadedConfig.referenceViewsUrl) {
          try {
            const refsResponse = await fetch(loadedConfig.referenceViewsUrl);
            if (refsResponse.ok && !cancelled) setRefs(await refsResponse.json());
          } catch {
            /* optional */
          }
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedPart = useMemo(
    () => doc?.parts.find((part) => part.part_id === selectedId) ?? null,
    [doc, selectedId],
  );

  const toggleProvenance = useCallback((state: GeometryProvenance) => {
    setHiddenProvenance((previous) => {
      const next = new Set(previous);
      if (next.has(state)) next.delete(state);
      else next.add(state);
      return next;
    });
  }, []);

  const toggleSystem = useCallback((system: string) => {
    setHiddenSystems((previous) => {
      const next = new Set(previous);
      if (next.has(system)) next.delete(system);
      else next.add(system);
      return next;
    });
  }, []);

  const togglePart = useCallback((partId: string) => {
    setHiddenParts((previous) => {
      const next = new Set(previous);
      if (next.has(partId)) next.delete(partId);
      else next.add(partId);
      return next;
    });
  }, []);

  const showAll = useCallback(() => {
    setHiddenSystems(new Set());
    setHiddenParts(new Set());
  }, []);

  const resetView = useCallback(() => {
    setSelectedId(null);
    setFocusToken((token) => token + 1);
  }, []);

  const selectPart = useCallback((partId: string | null) => {
    setSelectedId(partId);
    setFocusToken((token) => token + 1);
  }, []);

  const pickRef = useCallback((view: ReferenceView | null) => {
    setActiveRef(view);
    setNudge(NUDGE_IDENTITY);
    if (view) {
      setPoseNonce((n) => n + 1);
      setCompareMode((mode) => (mode === 'off' ? 'overlay' : mode));
    } else {
      setCompareMode('off');
    }
  }, []);

  if (error) {
    return (
      <div className="fatal">
        <h1>Viewer could not start</h1>
        <p>{error}</p>
        <p>
          Run <code>python scripts/build_control_skeleton.py</code> from the repository root to
          generate <code>viewer/public/control_skeleton.glb</code> and{' '}
          <code>viewer/public/parts.json</code>.
        </p>
      </div>
    );
  }

  if (!config || !doc) {
    return <div className="fatal">Loading control skeleton…</div>;
  }

  return (
    <div className="app">
      <Toolbar
        config={config}
        unitMode={unitMode}
        onUnitModeChange={setUnitMode}
        onResetView={resetView}
        onShowAll={showAll}
        panel={panel}
        onPanelChange={setPanel}
      />
      <div
        className={`body${leftCollapsed ? ' left-collapsed' : ''}${
          rightCollapsed ? ' right-collapsed' : ''
        }`}
      >
        <aside className={`left${leftCollapsed ? ' is-collapsed' : ''}`}>
          <button
            type="button"
            className="panel-toggle"
            onClick={() => setLeftCollapsed((value) => !value)}
            title={leftCollapsed ? 'Show the control skeleton panel' : 'Hide the control skeleton panel'}
            aria-expanded={!leftCollapsed}
          >
            {leftCollapsed ? '›' : '‹'}
          </button>
          {leftCollapsed && (
            <div className="panel-rail">
              <span>control skeleton</span>
            </div>
          )}
          <ProvenancePanel
            doc={doc}
            outlines={provenanceOutlines}
            onToggleOutlines={() => setProvenanceOutlines((value) => !value)}
            hidden={hiddenProvenance}
            onToggleProvenance={toggleProvenance}
          />
          <PartTree
            doc={doc}
            selectedId={selectedId}
            hiddenSystems={hiddenSystems}
            hiddenParts={hiddenParts}
            onSelect={selectPart}
            onToggleSystem={toggleSystem}
            onTogglePart={togglePart}
          />
          <ConfidenceLegend
            doc={doc}
            active={confidenceOverlay}
            onToggle={() => setConfidenceOverlay((value) => !value)}
          />
          <ReferencePanel references={config.references ?? []} />
          {refs && (
            <ComparePanel
              doc={refs}
              activeId={activeRef?.id ?? null}
              mode={compareMode}
              nudge={nudge}
              onPick={pickRef}
              onMode={setCompareMode}
              onNudge={(patch) => setNudge((n) => ({ ...n, ...patch }))}
              onRecall={() => setPoseNonce((n) => n + 1)}
              onReset={() => setNudge(NUDGE_IDENTITY)}
            />
          )}
          <div className="material-toggle">
            <label>
              <input
                type="checkbox"
                checked={materialMode}
                onChange={() => setMaterialMode((value) => !value)}
              />
              <span>Materials</span>
            </label>
            <p>
              Surfaces painted from the material assignments in GEOMETRY-CONTROL.md section 7.
              Turn off for the schematic view. The confidence overlay overrides this, so grades are
              never hidden behind a finish.
            </p>
          </div>
        </aside>
        <main className="stage">
          <ViewBar
            mode={viewMode}
            onModeChange={setViewMode}
            metresPerPixel={metresPerPixel}
            unitMode={unitMode}
            scaleDenominator={doc.ho_scale_denominator}
          />
          <BridgeViewer
            config={config}
            doc={doc}
            selectedId={selectedId}
            hiddenSystems={hiddenSystems}
            hiddenParts={hiddenParts}
            confidenceOverlay={confidenceOverlay}
            materialMode={materialMode}
            provenanceOutlines={provenanceOutlines}
            hiddenProvenance={hiddenProvenance}
            layoutToken={layoutToken}
            viewMode={viewMode}
            onScaleChange={setMetresPerPixel}
            onSelect={selectPart}
            focusToken={focusToken}
            pose={activeRef?.camera ?? null}
            poseNonce={poseNonce}
          />
          {activeRef && compareMode !== 'off' && (
            <CompareStage view={activeRef} mode={compareMode} nudge={nudge} />
          )}
          {photos && (
            <PhotoGallery manifest={photos} selectedId={photoId} onSelect={setPhotoId} />
          )}
          <PresentationNotice doc={doc} active={materialMode && !confidenceOverlay} />
          <footer className="stage-footer">
            <span>
              origin: {doc.coordinate_system.origin} · {doc.coordinate_system.x} ·{' '}
              {doc.coordinate_system.y} · {doc.coordinate_system.z}
            </span>
            <span>
              built from {doc.control_document.path} @ {doc.control_document.sha256.slice(0, 12)}
            </span>
          </footer>
        </main>
        <aside className={`right${rightCollapsed ? ' is-collapsed' : ''}`}>
          <button
            type="button"
            className="panel-toggle"
            onClick={() => setRightCollapsed((value) => !value)}
            title={rightCollapsed ? 'Show the part metadata panel' : 'Hide the part metadata panel'}
            aria-expanded={!rightCollapsed}
          >
            {rightCollapsed ? '‹' : '›'}
          </button>
          {rightCollapsed && (
            <div className="panel-rail">
              <span>{panel === 'metadata' ? 'part metadata' : 'dimensions'}</span>
            </div>
          )}
          {panel === 'metadata' ? (
            <MetadataPanel doc={doc} part={selectedPart} unitMode={unitMode} />
          ) : (
            <DimensionPanel doc={doc} unitMode={unitMode} />
          )}
        </aside>
      </div>
    </div>
  );
}
