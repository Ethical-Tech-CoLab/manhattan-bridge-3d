import { useEffect, useState } from 'react';

/**
 * Reference photographs, shown beside the model rather than over it, so the two can be compared.
 *
 * These are **visual reference only**. SOURCE-REGISTER.md marks the HAER photographs visual-only,
 * and STT-017 fails the build if any of them is ever cited by a control dimension. Nothing here is
 * aligned or registered to the model: no camera pose is known for any of these frames, so the
 * viewer deliberately offers no overlay or "match this view" — that would fabricate a registration
 * this project does not have.
 */

export interface Photo {
  id: string;
  file: string;
  caption: string;
  photographer: string;
  date: string;
  compare?: string;
}

export interface PhotoManifest {
  collection: string;
  sourceId: string;
  /** Stripped from thumbnail labels. Survey numbers repeat a long prefix on every frame. */
  idPrefix?: string;
  archive: { title: string; repository: string; url: string; rights: string };
  foundVia: { title: string; url: string; note: string };
  photos: Photo[];
}

function resolve(base: string, target: string): string {
  return new URL(target, new URL(base, window.location.href)).toString();
}

export function usePhotoManifest(url?: string) {
  const [manifest, setManifest] = useState<PhotoManifest | null>(null);
  useEffect(() => {
    // A module that publishes no photograph manifest gets no rail, and no request either. Asking
    // for a file that was never meant to exist would put a 404 in every reader's console.
    if (!url) {
      setManifest(null);
      return;
    }
    let cancelled = false;
    fetch(url)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((m: PhotoManifest) => {
        if (cancelled) return;
        setManifest({
          ...m,
          photos: m.photos.map((p) => ({ ...p, file: resolve(url, p.file) })),
        });
      })
      .catch(() => setManifest(null));
    return () => {
      cancelled = true;
    };
  }, [url]);
  return manifest;
}

export function PhotoGallery(props: {
  manifest: PhotoManifest;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}) {
  const { manifest, selectedId } = props;
  const selected = manifest.photos.find((p) => p.id === selectedId) ?? null;

  useEffect(() => {
    if (!selected) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') props.onSelect(null);
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        const i = manifest.photos.findIndex((p) => p.id === selected.id);
        const next =
          e.key === 'ArrowRight'
            ? (i + 1) % manifest.photos.length
            : (i - 1 + manifest.photos.length) % manifest.photos.length;
        props.onSelect(manifest.photos[next].id);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [selected, manifest.photos, props]);

  return (
    <>
      {selected && (
        <figure className="photo-pane">
          <button
            type="button"
            className="photo-close"
            onClick={() => props.onSelect(null)}
            aria-label="Close photograph"
          >
            ×
          </button>
          <img src={selected.file} alt={selected.caption} />
          <figcaption>
            <strong>{selected.id}</strong> · {selected.caption}
            <div className="subtle">
              {selected.photographer}, {selected.date}
            </div>
            {selected.compare && <p className="photo-compare">{selected.compare}</p>}
            <p className="photo-credit">
              {manifest.archive.title}.{' '}
              <a href={manifest.archive.url} target="_blank" rel="noreferrer">
                Library of Congress
              </a>
              . {manifest.archive.rights}
              <br />
              Surfaced by{' '}
              <a href={manifest.foundVia.url} target="_blank" rel="noreferrer">
                {manifest.foundVia.title}
              </a>
              , which carries many more.
            </p>
          </figcaption>
        </figure>
      )}

      <div className="photo-rail" role="listbox" aria-label="Reference photographs">
        <div className="photo-rail-head">
          <span>{manifest.collection}</span>
          <span className="subtle">reference only — grades nothing</span>
        </div>
        <div className="photo-strip">
          {manifest.photos.map((p) => (
            <button
              key={p.id}
              type="button"
              className={p.id === selectedId ? 'thumb on' : 'thumb'}
              onClick={() => props.onSelect(p.id === selectedId ? null : p.id)}
              title={`${p.id} — ${p.caption} (${p.photographer}, ${p.date})`}
              aria-selected={p.id === selectedId}
              role="option"
            >
              {/* Not lazy: the rail only mounts when the reader opens it, and all nine thumbnails
                  are visible at once, so deferring gains nothing. It also costs something — headless
                  Chromium defers lazy images even inside the viewport, which makes the gallery look
                  broken under test for a reason that has nothing to do with the gallery. */}
              <img src={p.file} alt={p.caption} />
              <span className="thumb-id">
                {manifest.idPrefix ? p.id.replace(manifest.idPrefix, '') : p.id}
              </span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
}
