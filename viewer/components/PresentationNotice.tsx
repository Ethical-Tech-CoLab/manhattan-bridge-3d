import type { PartsDocument } from '../src/model';

interface PresentationNoticeProps {
  doc: PartsDocument;
  active: boolean;
}

/**
 * On-screen statement that the render is illustrative ahead of survey.
 *
 * CONFIDENCE-MODEL.md section 7.3 requires this to live in the viewer and not only in the
 * documentation, on the reasoning that a render travels further than a methods section. A
 * screenshot of this model will end up in a slide deck; the caveat has to be inside the frame.
 */
export default function PresentationNotice({ doc, active }: PresentationNoticeProps) {
  if (!active) return null;
  const tally = (doc.measures.geometry_provenance_tally ?? {}) as Record<string, number>;

  return (
    <div className="presentation-notice">
      <strong>Illustrative render</strong>
      <p>
        Lighting, sky and haze are presentation only and carry no dimensional claim. The water plane
        is the exception: it sits at <code>z&nbsp;=&nbsp;0</code>, which is mean high water, a
        registered datum.
      </p>
      <p>
        Nothing here is measured — {tally.MEASURED ?? 0} parts. Tower arch openings, ornamental
        finials and truss web members are <em>not modelled</em>, so the structure is simpler than
        the bridge. Tracked as <code>OQ-021</code>, to be replaced by measured capture.
      </p>
    </div>
  );
}
