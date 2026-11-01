# Strict wording-only editing

Use this mode when the user asks for wording changes, asks to preserve logic, or limits edits to report highlights. The user's narrower constraints override the general repair workflow.

## Build the boundary automatically

Use the draft actually matched to the selected report. Read the visual highlights; never assume they cover whole paragraphs. Make one stable UTF-8 text snapshot and record its hash. Offsets refer to that exact snapshot. For DOCX, keep a mapping from text spans to paragraphs/runs; for PDF, retain page and text anchors. The user uploads files; the agent creates the manifest.

Record an edit contract privately:

- base file and text hash; authoritative report;
- authorized highlighted character spans;
- frozen unhighlighted spans, titles, captions, citations and references as applicable;
- mode: wording only; desired language level and audience;
- output format, required rubric functions, and any explicit target mark.

If a highlighted span covers only part of a sentence, freeze the rest. When the allowed boundary is unreadable, mark that portion unresolved and continue on readable spans. Do not guess a larger boundary.

## Permitted and excluded changes

Permitted: simpler word choices supported by the author's samples, idiomatic collocations, local grammatical repair, and clause rephrasing that leaves the same propositions, evidence and inference strength in place.

Preserve the argument, comparison units, facts, numbers, dates, citations, attribution, scope, modality, actors, sequence and paragraph order. Do not merge or delete propositions to create a new argument. Changing “suggests” to “proves,” “position” to “identity,” or “carry objects” to “stand carrying objects” changes more than wording. So does comparing people with their surroundings when the original compares arrangements across paintings.

Do not add observations, examples, personal experiences, research steps, new scholarship or new reasons for a claim. Existing logic problems are reported separately. Explicitly protected text stays frozen even if the agent thinks a correction would improve it.

When the user explicitly asks to revise every highlight, include each readable highlighted span in the review. Use the smallest natural change that preserves it; where only a conventional title or a fixed source name is highlighted, retain required names and identifiers and explain the constrained result rather than inventing replacement facts.

## Apply personal voice

Read the current evidence-based profile, not a generic list of banned AI words. Match ordinary verbs, pronoun use, clause relationships and transitions to actual samples. A writer may use long explanatory clauses, repeated technical nouns and genuine comparisons. Do not enforce short-sentence quotas, insert “I think,” add errors or swap correct words just for rarity.

The target mark is a scope preference. For a user seeking a clear undergraduate essay, prefer direct readable wording and preserve the existing analysis. Do not manufacture sophistication, strengthen claims, or deliberately reduce quality.

## Verify and stop

1. Reconstruct the candidate from the exact permitted replacements. The helper below catches edits outside highlights and changes to protected text.
2. Review every changed sentence against its original for meaning, certainty, attribution and comparison units.
3. Read preceding and following frozen sentences for antecedents and transitions. Resolve only within the authorized span.
4. Check original citations, captions, media and required content. Render the formatted artifact.
5. Deliver the revision and concise scope summary. Without a new matched report, label the new detector status untested. Stop after the authorized pass; repeated self-review should not become repeated full rewrites.

Run the bundled helper with agent-prepared private files:

```sh
python scripts/verify_wording_scope.py --before before.txt --after after.txt --manifest edits.json --output scope-check.json
```

Manifest shape: `allowed_spans` and `edits` are lists of objects with zero-based Unicode-code-point `start` and exclusive `end` offsets. Each allowed span has `original`; each edit has `before` and `after`. An edit must lie completely inside one allowed span. Allowed spans may be coalesced beforehand only if all intervening characters are also authorized. Insertions are allowed only strictly inside a highlighted span. A replacement may cover its full boundary. Files are read literally as UTF-8, including line endings.

The validator checks exact scope and source anchors. A successful result is not a grammar, truth, voice or detector assessment. Agent review supplies those separate checks.
