/**
 * Public surface of the shared bridge inspect shell.
 *
 * A module mounts <App /> and supplies everything else as data through model.config.json. The
 * individual panels are exported too, but a module that composes its own layout out of them has
 * begun a fork; prefer adding a data-gated feature here instead. See GOVERNANCE.md.
 */
export { default as App } from './App';
export { default as BridgeViewer } from './BridgeViewer';
export { default as ComparePanel } from './components/ComparePanel';
export { default as CompareStage } from './components/CompareStage';
export { default as ConfidenceLegend } from './components/ConfidenceLegend';
export { default as DimensionPanel } from './components/DimensionPanel';
export { default as MetadataPanel } from './components/MetadataPanel';
export { default as PartTree } from './components/PartTree';
export { PhotoGallery, usePhotoManifest } from './components/PhotoGallery';
export { default as PhotoAuditPanel } from './components/PhotoAuditPanel';
export { default as PresentationNotice } from './components/PresentationNotice';
export { default as ProvenancePanel } from './components/ProvenancePanel';
export { default as ReferencePanel } from './components/ReferencePanel';
export { default as Toolbar } from './components/Toolbar';
export { default as ViewBar } from './components/ViewBar';
export * from './model';
