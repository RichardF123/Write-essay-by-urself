# Content-controlled voice evidence and optional local steering

Use this reference when the user asks to separate topic from voice, test cross-topic transfer, or try activation steering. Ordinary paragraph editing continues to use the local evidence and checkpoint workflow. Users upload files; the agent prepares private datasets and runs the optional tools.

## First improve the evidence

Record a habit as an expression function with a source anchor: how an observation leads to a check, how a condition changes a comparison, or how a result supports a choice. List topic-specific nouns separately from transferable habits. Keep language and genre distinct; a casual Chinese post and an English academic report do not automatically share wording preferences.

To examine an uncertain habit, pair an eligible original passage with a neutral expression of the same content. Write a content contract first: facts, entities, quantities, conditions, causal links and claim strength. Review those dimensions against both texts. Do not make the neutral text more vague, stronger, shorter or less qualified merely to create a stylistic contrast. Record its generator and editorial role privately; it never becomes original author evidence. Existing grammatical errors can contaminate the extracted direction; correct candidate outputs rather than treating those errors as a target habit.

The pair makes topic control inspectable; it does not establish pure style. An original and an unrelated generic essay are not a useful contrast. Same prompt also does not guarantee same propositions. Preserve meaningful logical links even when they are part of the author's writing habits.

Report total pairs and independent families separately from the pairs and families actually used for extraction. With one training pair, alignment of that pair to its own direction is a construction property, not corroboration of a shared author style. Previously inspected evaluation material is development reuse. New synthetic topics can probe content preservation and topic leakage, but are not author-written holdout samples for measuring voice fit.

Write relation anchors explicitly, such as “interest in A is the reason for choosing B,” rather than listing the interest and choice as unrelated facts. Check that the candidate retains the connection and the target of each qualification. A list of preserved entities alone cannot establish preservation of reasoning.

Write that causal anchor only when the original supports it. A reason for wanting to learn about a company is not automatically an explicit reason for selecting the company. Preserve the reason's actual target. Likewise, considering an action is not completing it. If a source contains a substantive error or ambiguous research interpretation, quarantine that excerpt or resolve its suitability separately; do not alter its content on one side to manufacture a style pair.

### Construct a traceable original/rewrite pair

Freeze the exact original and its source offsets first. Ask the current agent or an available model for a neutral rewrite of that passage with the same facts, quantities, attribution, conditions, comparison, reasoning links, temporal stage and claim strength. Keep the original intact when revising a failed counterpart. The agent prepares these records; the user supplies samples.

For newly constructed pairs, add `pair_evidence` and run `voice_pairs.py` with `--require-pair-evidence`. Record the real generation instruction, raw response, model identifier (or explicitly `not_exposed`), date and method. Do not invent a separate API call when the current editing agent directly authors the rewrite. Retain exact editorial substitutions with reasons if the generated response is subsequently corrected. Preserve rejected or quarantined candidates privately, outside the extraction dataset, with reasons.

List each content-contract claim with exact anchors on both sides and a reasoned pass/fail judgment. Review the whole rewrite for added claims as well: matching the original claims alone does not detect an extra conclusion. Existing facts/conditions/causality/stance reviews still apply. Distinguish same-agent review from independent or blinded review. Multiple generator families can later test whether a direction captures one model's habits; record the actual count rather than assuming generalization.

The additional per-pair evidence schema is:

```json
{
  "pair_evidence": {
    "original_sha256": "SHA-256 of the exact original UTF-8 text",
    "neutral_sha256": "SHA-256 of the exact rewrite UTF-8 text",
    "generation": {
      "model": "Actual model identity or an explicit unavailable-identity description",
      "model_id_status": "known",
      "created_at": "ISO date or timestamp",
      "method": "Actual generation method",
      "prompt": "Actual rewrite instruction",
      "raw_response": "Original generated response",
      "edits": []
    },
    "reviewer": "Actual reviewing agent/person and independence status",
    "alignment": [
      {
        "claim_index": 0,
        "original_quote": "Exact anchor in the original",
        "neutral_quote": "Exact anchor in the rewrite",
        "status": "pass",
        "reason": "Specific comparison of this claim and its scope"
      }
    ],
    "addition_review": {
      "status": "pass",
      "reason": "Specific whole-rewrite check for added claims"
    }
  }
}
```

Use zero-based claim indices covering the entire `content_contract`. Each optional generation edit contains exact `before`, `after` and `reason`; replay must reproduce `neutral`. Hash changes invalidate the attached evidence. Legacy pairs remain readable without the strict flag; any supplied `pair_evidence` is always checked. Mechanical checks establish traceability and coverage of recorded judgments, not semantic equivalence. Archive the old vector when revising pairs, and re-extract before attributing any generation result to the revised dataset. Previously inspected test documents remain development reuse, not newly untouched evaluation.

## Validate pairs and evaluation splits

`scripts/voice_pairs.py` reads the existing owner-bound SQLite store without changing it. It checks original narrative bounds, confirmed authorship, source hashes, explicit semantic-review records, numerical tokens and requested exact literals. It separates document families, identical source snapshots and duplicate source text across train/validation/test. Store holdouts are test-only. One language and genre is allowed per dataset.

Each input pair contains:

```json
{
  "pair_id": "pair-01",
  "source_id": "original-01",
  "source_sha256": "exact source snapshot hash",
  "start": 0,
  "end": 42,
  "original": "exact selected narrative span",
  "neutral": "content-reviewed neutral expression",
  "split": "train",
  "topic": "orchard comparison",
  "content_contract": ["Same actors and observation; same conditional conclusion."],
  "protected_literals": ["an exact name or citation"],
  "review": {
    "facts": {"status": "pass", "reason": "Actual comparison performed."},
    "conditions": {"status": "pass", "reason": "Actual comparison performed."},
    "causality": {"status": "pass", "reason": "Actual comparison performed."},
    "stance": {"status": "pass", "reason": "Actual comparison performed."}
  }
}
```

This is a schema sketch; the agent supplies real offsets and content. Pass the list as `{"pairs": [...]}`. Review labels record agent judgments; numerical and provenance checks do not independently prove semantic equivalence. Number spelling changes require review and re-pairing rather than silently bypassing the conservative check.

```sh
python scripts/voice_pairs.py --db PRIVATE/voice.sqlite3 --owner WRITER --input PRIVATE/pairs.json --output PRIVATE/pairs-checked.json
```

For new traceable pairs, use:

```sh
python scripts/voice_pairs.py --db PRIVATE/voice.sqlite3 --owner WRITER --input PRIVATE/pairs.json --output PRIVATE/pairs-checked.json --require-pair-evidence
```

Choose splits by full document family before selecting layer, strength or preferred examples. Keep earlier holdouts protected. Count independent original families, eligible text, genres and topics, not just chunks. When material is sparse, call the result an engineering pilot and keep effectiveness unresolved. No fixed number of papers establishes sufficient personal-style evidence.

## Optional activation backend

`scripts/voice_steering.py` provides `baseline`, `extract` and `generate` for a model exposing `model.layers`, such as Qwen2.5 through Transformers. `baseline` needs no writing samples or style vector, so content fidelity can be inspected before extracting style. It uses the existing Python environment with torch and transformers when available; it does not install packages, download models or contact a remote service. An explicitly authorized remote experiment may run the same scripts in an isolated server workspace. Resolve its environment and upload only the necessary selected excerpts. Keep this dependency optional for the normal skill.

The pilot extracts the last-token layer activation from each original/neutral text, averages differences within each training family, then averages families and normalizes the vector. For paragraph-level PDF extraction it defaults to collapsing whitespace on both sides, while retaining exact originals in the provenance record; the chosen normalization is stored in the vector. This prevents PDF line wrapping or a trailing newline from being mistaken for personal style. Use `--text-normalization strip` or `none` only when preserving that whitespace is intentional. This is an explicitly recorded engineering choice, not an exact reproduction of StyleVector. It uses only train pairs for extraction and refuses silent truncation. It does not update model weights. The generation hook changes the last prefill position and subsequent cached generation positions; zero strength installs no hook and is checked against a separate unhooked run.

The vector records full local model/tokenizer file hashes, runtime, dtype, layer, dataset identity and extraction rule. Changing those conditions requires re-extraction and validation. This first backend supports BF16/FP32 eager execution; quantized or other model layouts need a separately tested implementation.

Before loading on a shared GPU, inspect current occupancy and use `--min-free-gib` with a suitable run-specific threshold (for example, `16` for the tested 7B BF16 setup). It checks free CUDA memory before loading; it is not a reservation and another job can still start afterward. Preserve failed-run logs, avoid repeated OOM retries, and wait for capacity or coordinate with the user. Do not terminate unrelated tasks to make room. The option is available on `baseline`, `extract` and `generate` and does not change the vector's numerical settings.

### Larger models and alternate inference adapters

The bundled backend operates on one locally loaded Transformers model. For an explicitly authorized multi-host experiment, prepare an isolated adapter with a fixed model, dtype and layer partition. Check GPU and disk capacity on each host, reuse completed downloads and verify shards against the publisher's hashes. Carry activations through the authorized encrypted connection with their dtype and bits preserved. Keep the adapter, source excerpts and model-specific vectors private while validating it.

Before using an alternate adapter for style judgments, compare its prefill and cached next-token logits against the standard implementation on a small compatible model at the intended dtype. Verify zero intervention and serialized activation round trips, then compare generated token IDs as well. Inspect the inherited generation configuration: greedy decoding can still apply a repetition penalty. Match that processor, EOS rules and prompt-history scope; raw-logit argmax alone may implement a different decoding rule. Record the actual decoding settings with each run. Re-extract for the larger model, then repeat the same content gate before style comparisons. Review each conditioning arm's zero-strength content separately, including RAG.

The stored direction has unit norm, so `--strengths 1` is not equivalent to multiplying an unnormalized difference by one in another paper. Use the recorded `raw_norm` to understand scale, then perform a bounded validation-only sweep while checking content and grammar. Identical greedy text at a weak strength establishes only that tested setting; do not infer a universal absence of effect or increase strength merely to force different wording.

```sh
python scripts/voice_steering.py baseline --model LOCAL_SNAPSHOT --tasks PRIVATE/validation-tasks.json --output PRIVATE/baseline.json
```

Review the baseline before the following steps:

```sh
python scripts/voice_steering.py extract --model LOCAL_SNAPSHOT --db PRIVATE/voice.sqlite3 --owner WRITER --input PRIVATE/pairs.json --layers 8 14 20 --output PRIVATE/vector.json
python scripts/voice_steering.py generate --model LOCAL_SNAPSHOT --db PRIVATE/voice.sqlite3 --owner WRITER --input PRIVATE/pairs.json --vector PRIVATE/vector.json --tasks PRIVATE/tasks.json --layer 14 --strengths 0 0.5 1 --output PRIVATE/generation.json
```

Tasks are `{"tasks": [...]}` with `task_id`, `language`, `genre`, and chat `messages`. Include only task content and authorized style evidence. The helper verifies model/runtime compatibility but does not decide the best layer or grade style. Keep extraction, validation and test tasks separated in the experiment plan. Read the resulting text and compare it with eligible anchors. Keep raw outcomes privately, including regressions.

## Compare methods before changing the default

First run `baseline` (or an existing vector's `generate --strengths 0`) on a small validation task with explicit observations and review it against the content contract. If the unsteered model reverses a fact, invents a motive, or merges separate scenes, qualify the content-generation setup before tuning style. Strengthen the content input or test a more capable base model, then repeat this baseline check. Outputs record whether generation ended with EOS or exhausted the token budget; a truncated passage is not a complete writing sample. A better-sounding steered answer does not repair an unqualified comparison. This is an agent semantic review, not an automatic verdict from token differences.

For essay refinement, include a faithful draft paragraph and explicit content anchors rather than relying only on a loose notes-to-paragraph request. Retain research-stage verbs, negative qualifications, comparison scope and separate scenes. If baseline feedback leads to a stronger instruction or content representation, preserve the earlier run and label the retest as development; do not call the revised tasks untouched held-out evaluation. Apply the same strengthened input to every comparison arm.

Keep the draft authoritative and separate editor checks from prose to be generated, for example with `<draft>` and `<editor_checks>` boundaries. Inspect for checklist leakage: a model may append “do not interpret this as …” or turn a private instruction into a sentence addressed to the reader. Such additions are editing failures, not an author's caution habit. Check explicit negative actions as well as positive ones, and distinguish “before recommending a change” from “before making a change.” A grammatical unchanged paragraph is an acceptable conservative result; a different output is not inherently an improvement.

Use the same model, content, generation budget and predeclared settings for plain generation, profile-only, RAG, steering and RAG-plus-steering. An initial narrow pilot may test only plain versus steering; report the missing comparisons. For a full evaluation, separately record user-blind style preferences, semantic preservation, task quality, grammar and topic-specific carryover. Add cross-topic inputs and, when justified, shuffled-pair or random-direction controls. Good authorship classification or low detector scores are not equivalent to a successful style transfer.

Steered text is a candidate. For a finished edit it still needs the original skill's semantic, voice, reader-facing and context reviews, exact authorized-span check, and artifact QA. A full generated paragraph cannot replace protected wording. Do not publish a feature as a measured voice improvement on the basis of successful extraction, changed token IDs, or one attractive output.

## Research basis

- [John et al., ACL 2019](https://aclanthology.org/P19-1041/): learned content/style separation.
- [Konen et al., EACL Findings 2024](https://aclanthology.org/2024.findings-eacl.52/): style vectors at hidden layers.
- [Zhang et al., ACL 2025](https://aclanthology.org/2025.acl-long.353/): personalized contrastive activation steering and its remaining disentanglement limits.
- [Topic Confusion, 2021](https://aclanthology.org/2021.findings-emnlp.359/): topic shortcuts in author evaluation.
- [Tan et al.](https://arxiv.org/abs/2407.12404): steering reliability depends on input and prompt conditions.

These works motivate the experiment; the scripts are a small local pilot with their own recorded execution choices.
