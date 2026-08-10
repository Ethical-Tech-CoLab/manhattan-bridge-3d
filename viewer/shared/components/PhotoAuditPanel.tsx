import type { PhotoAudit } from '../model';

interface PhotoAuditPanelProps {
  audit?: PhotoAudit;
}

/**
 * Link out to the human-in-the-loop photograph audit.
 *
 * The audit exists because the automatic screen could not do the job and should not have pretended
 * to: measured across the first corpus, sky coverage ran 0.16-0.79 for interiors and 0.51-1.00 for
 * exteriors, so any threshold that caught the interiors also discarded good street views. A person
 * decides instead, and until one has looked, a photograph stays `auto_screened` and is carried as
 * weaker evidence -- never silently promoted, never silently dropped.
 *
 * Surfacing that from the viewer matters because the audit is the step where evidence becomes
 * citable. A reader who wants to know why a part is graded the way it is should be one click from
 * the sheet where that judgement was recorded.
 *
 * Data-gated: a module that publishes no audit gets no panel, rather than a link to a 404.
 */
export default function PhotoAuditPanel({ audit }: PhotoAuditPanelProps) {
  if (!audit) return null;

  const { reviewed, total } = audit;
  const hasCounts = typeof reviewed === 'number' && typeof total === 'number' && total > 0;

  return (
    <section className="audit-panel">
      <a className="audit-link" href={audit.url} target="_blank" rel="noreferrer noopener">
        <span className="audit-title">{audit.label ?? 'Photograph audit'}</span>
        <span className="audit-arrow" aria-hidden="true">
          ↗
        </span>
      </a>
      {hasCounts && (
        <p className="audit-counts">
          <strong>
            {reviewed} of {total}
          </strong>{' '}
          photographs reviewed by a person
          {reviewed < total && <span className="audit-pending"> · {total - reviewed} still auto-screened</span>}
        </p>
      )}
      <p className="audit-note">
        {audit.note ??
          'A person decides what each photograph can inform. Until one has, a record stays auto-screened and counts as weaker evidence.'}
      </p>
    </section>
  );
}
