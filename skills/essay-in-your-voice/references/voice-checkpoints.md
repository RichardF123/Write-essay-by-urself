# Voice checkpoints during revision

These checkpoints connect original evidence to actual editing decisions. The skill's agent orchestrates them with `scripts/voice_rag.py` and ordinary review; they are not mandatory host hooks and do not intercept every generated token. Read [local-retrieval.md](local-retrieval.md) for private intake, commands and packet fields. Respect analysis-only requests: preparing evidence does not authorize revision.

## 1. Before proposing a change

Freeze the latest authorized base text and derive exact allowed spans from the user's scope and matched report, never from retrieval results. State the passage's job, current propositions, comparison units, uncertainty and nearby antecedents. Identify a concrete problem before changing it. Highlighting alone is insufficient.

Retrieve a small set of eligible original anchors matching the target language, genre and rhetorical function. Read their context and identify the specific transferable habit: how the author joins a reason to a claim, compares objects or limits an inference. A cross-topic example may support sentence organization without supplying topical facts. Respect the one-chunk-per-family cap and held-out exclusions. Treat a profile's claims as hypotheses until its anchors are checked.

Build a packet containing the fixed text, authorized spans, current brief, scoped preferences and retrieved evidence. Include only current writing instructions in the writer's brief. Store editing history and rejected candidates in revision memory. Without usable originals, narrow the claim to preference-based editing and retain an unresolved voice judgment when needed.

## 2. After drafting a local candidate

Review the candidate against the original and record four independent judgments:

| Review key | Required check |
| --- | --- |
| `semantics` | Preserve propositions, actors, facts, citations, comparison units, inference strength and substantive objections within the current scope. |
| `voice` | Explain which eligible original anchors support the changed vocabulary, clause relationship or stance; cite evidence IDs for a pass when evidence exists. Do not infer voice fit from generic simplicity. |
| `reader_facing` | Present the current argument for its reader. Check editing-history leakage, invented objections, redundant negations and stacked qualifiers by function; preserve material uncertainty and real counterarguments. |
| `context` | Read preceding and following text for antecedents, transitions, repetition and paragraph purpose. Resolve problems only inside allowed spans. |

Each key has `status: pass`, `fail` or `unknown`, plus a concrete `reason`. Evidence absence is not a pass. An exact excerpt match is not a semantic verdict. Apply [reader-facing-prose.md](reader-facing-prose.md) inside the existing boundary; do not remove a substantive limitation merely to make prose more direct.

Run `audit` with the packet, candidate, edit manifest and review. The deterministic scope check must reconstruct the candidate exactly and preserve every protected character. A ready result additionally requires all four reviews to pass; the script records these agent judgments rather than independently proving them.

## 3. On a failed or unresolved check

For a scope failure, restore protected text and repair only the permitted substitutions. For changed meaning, restore the original claim strength or reject the candidate. For a voice failure, reread the relevant original anchors and sentence function before another attempt. For reader-facing leakage, move drafting explanations to the revision log when the authorized span permits removal. For a contextual issue outside scope, report it separately.

Do not expand the editable boundary to make a failed candidate fit. Do not switch to generic humanizing rules, add errors, invent personal experience or promote an assistant revision into original evidence. When evidence remains insufficient, preserve the original wording where appropriate and deliver the bounded work with the unresolved judgment stated. An unchanged candidate can be the justified outcome; it must not receive a fabricated ready result.

## 4. Before delivery and when the user corrects the voice

Review the assembled draft once for paragraph purpose, calibrated claims, reader-facing relevance and coherence. Confirm that the delivered text is the audited candidate, and use the host's artifact/rendering tools when a formatted document is requested. Keep detailed evidence and rejected edits in private supporting records; give the user the requested draft and a concise account of material limitations. A detector outcome remains untested without a new matching report.

If the user says the result still sounds unlike them, return to the original anchors and relevant context before rewriting. Store an explicit new preference with its scope; distinguish it from an observed habit. Refresh the packet if the brief, base text, permitted spans or eligible evidence changes. Complete the authorized pass and stop; checkpoints are safeguards for decisions, not a reason to run endless full-document rewrites.
