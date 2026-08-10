import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from '../shared';
import '../shared/styles.css';

/**
 * Module entry point. This file and the JSON under public/ are the only viewer code this
 * repository owns; everything in viewer/shared/ is vendored from digital-3d-shared-contracts and
 * is verified against VIEWER-UI.sha256 on every build. See GOVERNANCE.md.
 */
const container = document.getElementById('root');
if (!container) throw new Error('#root is missing from index.html');

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);