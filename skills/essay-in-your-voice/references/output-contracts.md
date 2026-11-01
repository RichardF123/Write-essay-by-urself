# Private task-output contracts

Use only the outputs needed for the requested scope. These are compact schemas, not templates to fill with invented information. Explain unknowns. Do not publish these files with the skill.

## voice-profile.md

- Corpus and authorship scope; target language/genre; excluded material; limitations.
- Per habit: rule | sample/page/paragraph | evidence anchor | recurrence | counterexample | confidence | transfer to target.
- User-stated preferences distinct from observed patterns.
- Calibration/holdout outcome if actually performed; version/date of profile.

## report-ledger.md

- Report metadata and verified draft mapping; observed score/coverage; mapping confidence.
- Stable paragraph/span ID | round | report page/anchor | actual text | highlight extent | readability.
- Cross-round: text changed? | exact/rewritten/split/merge/uncertain | highlight transition | content assessment | attribution limits.

## highlight-patterns.md

- Phenomenon | locatable cases/round count | comparison method | author-style match | image/source issues | counterexamples | content implication | observed report association | confidence.
- Separate one-off observations from repeated patterns. Never invent a detection-risk percentage.

## paragraph-audit.md

| ID | paragraph function | observation/source → inference | image/text scope | evidenced voice mismatch | report state | rubric role | keep/edit/verify and why |
| --- | --- | --- | --- | --- | --- | --- | --- |

Cover every body paragraph. “Keep, no specific problem found” is a valid decision. Do not force a criticism into every row. Mark citation/caption/reference-list checks separately rather than silently excluding them.

## revision-log.md

- Base and revised versions/hashes, protected paragraphs, intended scope.
- Each change: paragraph ID, original exact span, replacement, reason grounded in evidence, facts/citations/uncertainty retained, relevant rubric check.
- Exact comparison of protected text; exceptions and why necessary.
- Report status: matching fresh report / untested / unknown, without a promised score.

## rubric-check.md

Requirement verbatim or faithfully summarized | source location | evidence in draft | satisfied/not satisfied/unverified/not applicable | required action.

Use actual word-count rules; distinguish main text from captions, references and cover/reflection. Source ratios need an explicit denominator. An estimated grade requires the actual rubric and a stated uncertainty range, never an assured mark.

## preflight-assessment.md

- Available evidence: original samples, unique report submissions, independent essay families, tool/model/genre comparability, score states and known disagreements.
- Paragraph | author fit | highlight tendency | confidence and basis | matched analogue | counterexample | warranted action within current scope.
- Observed report percentages and historical coverage kept distinct from the preflight labels.
- Calibration status and held-out error only if a predictor was actually fitted/evaluated; otherwise qualitative assessment.

## wording scope manifest and check

- The agent generates exact text snapshots, authorized character spans and replacements from the selected report.
- `verify_wording_scope.py` verifies that every edit lies within authorization and reconstructs the exact candidate. Report protected text as preserved only after this or an equivalent exact check passes.
- Manual semantic check: facts, comparisons, uncertainty, attribution, causal relations and neighboring frozen sentences.
- Record the requested target language level/mark as effort guidance, separately from actual rubric assessment.
