# Decision-model recommendation: source-review prioritization

Date: 2026-10-11. Public-source proposal.
Reviewed [README](https://github.com/Ethical-Tech-CoLab/manhattan-bridge-3d/blob/e5ddb9b14eb1fb31c69135e6c0ca11cc015b428f/README.md)
and the source-governance handoff. This is a documentation-led assessment.

## Fit and retained authority

Use an optional offline assessor to rank registered source passages by
relevance to a named open geometry question or flag mismatched source/part
references. Output relevance plus insufficient evidence, retaining source IDs.
Do not ask a model to infer dimensions from photographs or plausible meshes.

The geometry-control document, source register, weakest-link grades and named
placeholders remain authoritative. Auto-screened photos are not human-reviewed.
Do not promote image agreement into a grade upgrade or claim schema validation
ran when the current CI explicitly skips it.

## Evaluation

Compare exact part/source lookup and lexical retrieval with a local reranker,
Jev's [reranking recipe](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md),
Microsoft-Decision-1 and Sage on public documents. Split by source/part family;
include conflicting cable dimensions, unposed imagery, missing drawings and
similar neighboring components.

Measure candidate recall, NDCG, unsupported dimension-support claims,
calibration, reviewer time and total accepted-source cost. Pointwise relevance
can be sorted deterministically; a score is not a measurement or source grade.

## Gate and impact

No generated geometry, shared viewer code, schema or confidence grades change.
Only derived review suggestions may be added after human approval. A future
geometry change must pass existing traceability tests and actual schema checks.
Exact proprietary checkpoints are not local; separately licensed local models
are valid alternatives. No measured saving is claimed.
