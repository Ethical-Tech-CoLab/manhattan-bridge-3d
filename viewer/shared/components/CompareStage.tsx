import { useCallback, useEffect, useRef, useState } from 'react';
import type { CompareMode, Nudge, ReferenceView } from '../model';

interface Props {
  view: ReferenceView;
  mode: Exclude<CompareMode, 'off'>;
  nudge: Nudge;
}

/**
 * Puts the reference image either over the 3D viewport or beside it.
 *
 * Rendered as an absolutely-positioned layer rather than as a wrapper around the viewport. Wrapping
 * would force every module's stage into one DOM shape; overlaying leaves the stage alone, so a
 * module that also shows a view bar, a scale bar and a presentation notice keeps all three.
 *
 * Overlay uses a plain CSS transform rather than projecting the image into the scene: the pose is
 * approximate by construction, so a reader needs to be able to slide the image around by hand, and
 * a screen-space transform is the honest tool for that. Nothing here feeds back into the model.
 */
export default function CompareStage({ view, mode, nudge }: Props) {
  const [split, setSplit] = useState(0.5);
  const [aspect, setAspect] = useState<number | null>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);

  // The overlay is only meaningful if the model letterboxes exactly as the image does. Measuring
  // the image's natural aspect and constraining the 3D viewport to match is what makes a drawing
  // overlay line up instead of merely sitting on top.
  useEffect(() => {
    setAspect(null);
    const img = new Image();
    img.onload = () => setAspect(img.naturalWidth / img.naturalHeight);
    img.src = view.image;
  }, [view.image]);

  const onMove = useCallback((clientX: number) => {
    const el = stageRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const t = (clientX - rect.left) / rect.width;
    setSplit(Math.min(0.9, Math.max(0.1, t)));
  }, []);

  useEffect(() => {
    const move = (e: MouseEvent) => {
      if (draggingRef.current) onMove(e.clientX);
    };
    const up = () => {
      draggingRef.current = false;
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    return () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
  }, [onMove]);

  if (mode === 'overlay') {
    return (
      <div className="compare-layer overlay" ref={stageRef}>
        <div
          className="overlay-image"
          style={{
            opacity: nudge.opacity,
            aspectRatio: aspect ? String(aspect) : undefined,
            transform: `translate(${nudge.dx}%, ${nudge.dy}%) scale(${nudge.scale})`,
          }}
        >
          <img src={view.image} alt={view.title} />
        </div>
        <p className="stage-credit">{view.credit}</p>
      </div>
    );
  }

  // Split mode masks the left portion of the viewport with the reference image. The model is not
  // moved or re-rendered; it is simply covered, which is why the divider can be dragged freely.
  return (
    <div className="compare-layer split" ref={stageRef}>
      <div className="split-pane reference" style={{ width: `${split * 100}%` }}>
        <div
          className="split-image"
          style={{ transform: `translate(${nudge.dx}%, ${nudge.dy}%) scale(${nudge.scale})` }}
        >
          <img src={view.image} alt={view.title} />
        </div>
        <p className="stage-credit">{view.credit}</p>
      </div>
      <div
        className="split-handle"
        role="separator"
        aria-label="drag to compare"
        aria-valuenow={Math.round(split * 100)}
        tabIndex={0}
        onMouseDown={() => {
          draggingRef.current = true;
        }}
        onKeyDown={(e) => {
          if (e.key === 'ArrowLeft') setSplit((s) => Math.max(0.1, s - 0.02));
          if (e.key === 'ArrowRight') setSplit((s) => Math.min(0.9, s + 0.02));
        }}
      />
    </div>
  );
}
