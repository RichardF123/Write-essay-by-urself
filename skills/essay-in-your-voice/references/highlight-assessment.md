# Evidence-based highlight tendency

This mode answers a request for a rough AI-rate judgment with the evidence the task actually provides. Its default output is a paragraph review, not a synthetic detector score.

## Separate three outputs

| Output | Evidence | Meaning |
| --- | --- | --- |
| Author fit | Original samples, genre and user feedback | How well wording and reasoning match this writer |
| Highlight tendency | Verified prior reports and comparable passages | How closely the passage resembles patterns highlighted in the available history |
| Observed report percentage | The actual matched report | The score produced on that submission |

An author's normal wording may be highlighted. An unhighlighted passage may be unlike the author. Do not map either result onto authorship, quality, or the other axis.

## Construct the evidence from uploads

Read the report-comparison protocol first. Group revisions, exports and formatting variants of one underlying essay into a document family. Deduplicate copies of the same submission. Distinguish the same visible prose from an identical submitted file: extracting matching paragraphs does not establish byte identity, identical parsing or model conditions.

Retain tool, language, genre, disclosed model/version, report date, coverage definition and score state. Unknown model versions stay unknown. A hidden score is censored, not zero or its threshold. A report with hidden highlights supplies no negative labels for individual sentences.

The case experience behind this package includes:

- matching visible body prose with a suppressed result in one submission and an above-threshold result in another;
- substantial argument revision with little overall score change;
- a later wording-only round with a larger observed decrease;
- unchanged sentences acquiring highlights, alongside revised text losing highlights.

These are counterexamples to simplistic rules, not training labels proving how another writer will score. One essay with many reports is one correlated case family.

## Make the review

For each paragraph return:

- author fit: aligned / partly aligned / evidence thin;
- highlight tendency: lower resemblance / mixed / higher resemblance / insufficient evidence;
- report analogues: locators, changed/unchanged status, similar and counterexample passages;
- confidence: strong/moderate/weak evidence **for this comparison**, with the basis;
- relevant expression patterns and whether an edit is within scope.

Use higher resemblance only when recurring, locatable patterns in comparable verified reports support it. A generic dislike of a word or a tidy sentence does not suffice. Lower resemblance needs positive comparison evidence, not merely the absence of a keyword. Mark insufficient evidence when there are no suitable reports; a personal-style review can still proceed.

Do not average these labels into a whole-document AI percentage. A proportion of paragraphs reviewed, a proportion of highlighted visible words, a similarity score and the detector's qualifying-text percentage have different denominators. Label any descriptive coverage statistic by its actual method.

## When numerical forecasting becomes supportable

A predictor needs independent document families, verified report labels, comparable detection conditions, a defined input representation, and held-out evaluation. Split by essay family, and by author where the intended claim is cross-author. Keep repeated paragraphs and revised descendants out of opposite sides of the split. Do not train on the report being predicted or on its later revisions.

Assess prediction error and prediction-interval coverage on the held-out cases; document sample size, model, scoring denominator, uncertainty and out-of-domain behavior. Handle censored scores with a method that represents censoring, not made-up labels. If conditions drift, reassess calibration. A few reports from this session provide longitudinal case evidence, not such a fitted/calibrated model.

If a calibrated predictor is actually available, report a broad prediction interval with the measured error and applicable domain, separately from authorship. Otherwise provide observed history and qualitative tendency. Never fabricate a point such as “probably 24%” from a prose impression, counts of AI-sounding words, or a made-up 0–100 risk score.

## Private metadata helper

The agent can use `scripts/summarize_report_history.py` to summarize uploaded reports. It records score observations, duplicate submissions and same-prose disagreements without reading or publishing essay prose. It fits no prediction model.

Input is an agent-generated JSON list (or an object containing `reports`) with:

`report_id`, `family_id`, `tool`, `score` (`number`, or `{"state":"suppressed","below":20}`), optional `submission_id`, `language`, `genre`, `model_version`, `prose_fingerprint`, `submitted_file_sha256`, `report_date`.

`prose_fingerprint` hashes the declared normalized body scope, not the original file. Keep normalization method and scope in the private ledger. When duplicate IDs have conflicting metadata or scores, surface the conflict rather than silently dropping a result. Never upload these local records simply because an assessment was requested.

## Sources

Turnitin describes its percentage as applying to qualifying prose and distinguishes it from similarity scores: https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report

Suppressed scores hide both the exact percentage and source highlights: https://helpcenter.turnitin.com/hc/en-us/articles/46245332050317-Why-is-the-AI-Writing-Detection-report-score-showing-as

Use these definitions when interpreting supplied reports; they do not expose a causal rule for any particular wording pattern. Source check: 2026-11-01.
