# Content-controlled voice evidence and optional local steering

Use this reference when the user asks to separate topic from voice, test cross-topic transfer, or try activation steering. Ordinary paragraph editing continues to use the local evidence and checkpoint workflow. Users upload files; the agent prepares private datasets and runs the optional tools.

## First improve the evidence

Record a habit as an expression function with a source anchor: how an observation leads to a check, how a condition changes a comparison, or how a result supports a choice. List topic-specific nouns separately from transferable habits. Keep language and genre distinct; a casual Chinese post and an English academic report do not automatically share wording preferences.

To examine an uncertain habit, pair an eligible original passage with a neutral expression of the same content. Write a content contract first: facts, entities, quantities, conditions, causal links and claim strength. Review those dimensions against both texts. Do not make the neutral text more vague, stronger, shorter or less qualified merely to create a stylistic contrast. Record its generator and editorial role privately; it never becomes original author evidence. Existing grammatical errors can contaminate the extracted direction; correct candidate outputs rather than treating those errors as a target habit.

The pair makes topic control inspectable; it does not establish pure style. An original and an unrelated generic essay are not a useful contrast. Same prompt also does not guarantee same propositions. Preserve meaningful logical links even when they are part of the author's writing habits.

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

Choose splits by full document family before selecting layer, strength or preferred examples. Keep earlier holdouts protected. Count independent original families, eligible text, genres and topics, not just chunks. When material is sparse, call the result an engineering pilot and keep effectiveness unresolved. No fixed number of papers establishes sufficient personal-style evidence.

## Optional activation backend

`scripts/voice_steering.py` provides `extract` and `generate` for a local model exposing `model.layers`, such as Qwen2.5 through Transformers. It uses the existing Python environment with torch and transformers when available; it does not install packages, download models or use a remote service. Resolve the needed environment in the user's task. Keep this dependency optional for the normal skill.

The pilot extracts the last-token layer activation from each original/neutral text, averages differences within each training family, then averages families and normalizes the vector. For paragraph-level PDF extraction it defaults to collapsing whitespace on both sides, while retaining exact originals in the provenance record; the chosen normalization is stored in the vector. This prevents PDF line wrapping or a trailing newline from being mistaken for personal style. Use `--text-normalization strip` or `none` only when preserving that whitespace is intentional. This is an explicitly recorded engineering choice, not an exact reproduction of StyleVector. It uses only train pairs for extraction and refuses silent truncation. It does not update model weights. The generation hook changes the last prefill position and subsequent cached generation positions; zero strength installs no hook and is checked against a separate unhooked run.

The vector records full local model/tokenizer file hashes, runtime, dtype, layer, dataset identity and extraction rule. Changing those conditions requires re-extraction and validation. This first backend supports BF16/FP32 eager execution; quantized or other model layouts need a separately tested implementation.

```sh
python scripts/voice_steering.py extract --model LOCAL_SNAPSHOT --db PRIVATE/voice.sqlite3 --owner WRITER --input PRIVATE/pairs.json --layers 8 14 20 --output PRIVATE/vector.json
python scripts/voice_steering.py generate --model LOCAL_SNAPSHOT --db PRIVATE/voice.sqlite3 --owner WRITER --input PRIVATE/pairs.json --vector PRIVATE/vector.json --tasks PRIVATE/tasks.json --layer 14 --strengths 0 0.5 1 --output PRIVATE/generation.json
```

Tasks are `{"tasks": [...]}` with `task_id`, `language`, `genre`, and chat `messages`. Include only task content and authorized style evidence. The helper verifies model/runtime compatibility but does not decide the best layer or grade style. Keep extraction, validation and test tasks separated in the experiment plan. Read the resulting text and compare it with eligible anchors. Keep raw outcomes privately, including regressions.

## Compare methods before changing the default

First run a zero-strength-only control (`generate --strengths 0`) on a small validation task with explicit observations and review it against the content contract. If the unsteered model reverses a fact, invents a motive, or merges separate scenes, qualify the content-generation setup before tuning style. Strengthen the content input or test a more capable base model, then repeat this baseline check. A better-sounding steered answer does not repair an unqualified comparison. This is an agent semantic review, not an automatic verdict from token differences.

Use the same model, content, generation budget and predeclared settings for plain generation, profile-only, RAG, steering and RAG-plus-steering. An initial narrow pilot may test only plain versus steering; report the missing comparisons. For a full evaluation, separately record user-blind style preferences, semantic preservation, task quality, grammar and topic-specific carryover. Add cross-topic inputs and, when justified, shuffled-pair or random-direction controls. Good authorship classification or low detector scores are not equivalent to a successful style transfer.

Steered text is a candidate. For a finished edit it still needs the original skill's semantic, voice, reader-facing and context reviews, exact authorized-span check, and artifact QA. A full generated paragraph cannot replace protected wording. Do not publish a feature as a measured voice improvement on the basis of successful extraction, changed token IDs, or one attractive output.

## Research basis

- [John et al., ACL 2019](https://aclanthology.org/P19-1041/): learned content/style separation.
- [Konen et al., EACL Findings 2024](https://aclanthology.org/2024.findings-eacl.52/): style vectors at hidden layers.
- [Zhang et al., ACL 2025](https://aclanthology.org/2025.acl-long.353/): personalized contrastive activation steering and its remaining disentanglement limits.
- [Topic Confusion, 2021](https://aclanthology.org/2021.findings-emnlp.359/): topic shortcuts in author evaluation.
- [Tan et al.](https://arxiv.org/abs/2407.12404): steering reliability depends on input and prompt conditions.

These works motivate the experiment; the scripts are a small local pilot with their own recorded execution choices.
