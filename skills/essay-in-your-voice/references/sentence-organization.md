# Calibrating sentence organization across revisions

Read this when the user asks for personal sentence structure, rejects a style match, or keeps returning with highlighted passages. Keep the current edit contract; this reference does not authorize argument repair.

## Re-anchor before another pass

Reread the existing voice profile and a few relevant original passages. Choose passages that perform the same job as the target: explaining an observation, comparing conditions, using a source, limiting a judgment or choosing a method. Record a locator and the relationship each anchor demonstrates. An earlier assistant-written trial is a candidate, not original evidence.

Keep these distinct:

- **Observed habit:** supported by originals, with genre and counterexamples.
- **User preference:** explicitly requested, even when sample evidence is thin.
- **Editorial choice:** proposed for this passage, evaluated for meaning and readability.
- **Report observation:** a visible highlight transition in matched submissions.

Do not turn the originating author's habits into defaults for every user. A formal project may contain both ordinary verbs and technical vocabulary; notes may have different syntax from an essay.

## Diagnose the organization, not just the words

For an in-scope passage, map its existing propositions and relationships before rewriting. A useful private sketch is `observation → interpretation → check → judgment`, but use the sequence actually supported by this author and paragraph. Mark what each sentence adds, which noun a pronoun refers to, and where the reader must infer a link.

| Candidate mismatch | Check against originals and context | Possible local response |
| --- | --- | --- |
| Each sentence restarts the same person or object | Does the author normally keep related observations in one clause chain? | Connect related clauses or use a clear pronoun; retain every observation. |
| A method is announced after analysis has already begun | Does it explain a real choice or merely restate nearby evidence? | Express the existing choice directly or connect it to the reason already present. |
| General difference followed by the same difference as an example | Does the second sentence add a proposition? | Link the general statement and example without dropping required information. |
| Evidence and its consequence are detached | Is the consequence already established, or only plausible? | Make the existing relationship explicit; do not invent a causal link. |
| Repeated balanced comparisons | Do the author's contrasts serve this function, or are they an editor's preferred cadence? | Vary the organization only where evidence supports it; preserve genuine comparisons. |
| Repeated ordinary nouns | Is repetition keeping the argument clear? | Keep useful repetition; avoid decorative synonyms. |

Neither joining nor splitting sentences is a goal. Do not use sentence-length or connector quotas. Adding `which`, `so`, `From the figure` or `I think` without a function imitates surface features rather than reasoning. Removing first person can replace a direct choice with a more abstract phrase such as `provides the basis for comparison`; evaluate both versions rather than assuming the replacement improves voice.

## Preserve the inferential contract

Sentence organization may connect or locally rearrange existing clauses only when the user permits that scope and no proposition, comparison unit, source attribution, uncertainty or logical dependency changes. Historical sequence and actual research steps remain fixed. If the user freezes sentence or analysis order, choose an in-order rephrase instead.

List the old and new propositions side by side for a multi-sentence edit. Check specifically:

- Adjacent facts are not automatically a cause and consequence; `so` needs an already supported relationship.
- A visible pose, spacing or outline is not itself proof of an activity, identity, feeling or intention.
- A literature statement about topics does not automatically support a claim about composition, rank or causation.
- A relative clause keeps the original attribution and a clear antecedent.
- No added detail fills an evidence gap just to make prose smoother.

In highlighted-only mode, each multi-sentence edit must fit a visually verified continuous editable span, including intervening text. Never bridge a protected sentence or silently treat an entire paragraph as highlighted. Keep exact snapshots for `verify_wording_scope.py`.

## Retain, revise or roll back

Keep a compact revision memory: passage ID, proposed change, original anchor, expected writing benefit, semantic check, user feedback and later report status. Judge a candidate against its immediate predecessor and the original anchors; repeated paraphrasing can gradually drift away from both.

Retain a clearer sentence even if it stays highlighted. Roll back an edit that becomes less natural, more abstract, ambiguous or inaccurate even if a nearby highlight disappears. Avoid cycling between the same formulations without new writing evidence. A report without a specific expression problem is a valid reason to keep wording.

For a targeted request, audit all requested locations but edit only justified ones; record why a reviewed location is retained. Do not invent a fixed number of edits. Stop after the authorized pass and delivery. A user can request another pass, but continuing should respond to new feedback or a concrete unresolved issue rather than an automatic resubmission loop.
