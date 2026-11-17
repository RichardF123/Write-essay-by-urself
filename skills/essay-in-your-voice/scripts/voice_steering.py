"""Optional local activation-steering pilot. Requires installed torch/transformers."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import time

from voice_pairs import digest, read_json, require, validate_dataset, write_new


def model_identity(path):
    root = Path(path).resolve()
    require(root.is_dir(), 'Provide a local model snapshot directory; no automatic downloads.')
    files = sorted(p for p in root.iterdir() if p.is_file() and
                   (p.suffix in {'.json', '.safetensors', '.bin', '.model'} or p.name == 'merges.txt'))
    require(any(p.name == 'config.json' for p in files), 'Model config is missing.')
    weights = [p for p in files if p.suffix in {'.safetensors', '.bin'}]
    require(bool(weights), 'Local model weights are missing.')
    hashes = {}
    for p in files:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
                h.update(chunk)
        hashes[p.name] = h.hexdigest()
    return {'files_sha256': hashes, 'model_sha256': digest(hashes)}


def load_model(path, dtype, device, cpu_threads=1):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    require(type(cpu_threads) is int and cpu_threads > 0, 'CPU thread count must be positive.')
    torch.set_num_threads(cpu_threads)
    require(device != 'cuda' or torch.cuda.is_available(), 'CUDA is unavailable.')
    tok = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        path, local_files_only=True, trust_remote_code=False,
        torch_dtype=getattr(torch, dtype), attn_implementation='eager').to(device)
    model.eval().requires_grad_(False)
    require(hasattr(model, 'model') and hasattr(model.model, 'layers'),
            'This pilot supports models exposing model.layers (e.g. Qwen2.5).')
    return torch, tok, model, {'torch': torch.__version__, 'transformers': transformers.__version__,
                               'dtype': dtype, 'device': device, 'attention': 'eager',
                               'cpu_threads': cpu_threads}


def output_tensor(output):
    return output[0] if isinstance(output, tuple) else output


def extraction_text(text, mode):
    if mode == 'collapse-whitespace':
        return ' '.join(text.split())
    if mode == 'strip':
        return text.strip()
    require(mode == 'none', 'Unknown extraction text normalization.')
    return text


def finish_reason(tokens, eos_ids, limit):
    ids = eos_ids if isinstance(eos_ids, (list, tuple)) else [eos_ids]
    if tokens and tokens[-1] in ids:
        return 'eos'
    return 'length' if len(tokens) >= limit else 'other'


@contextmanager
def intervention(layer, vector, strength):
    require(math.isfinite(strength), 'Strength must be finite.')
    # No hook at zero: preserves the unmodified numerical execution path.
    if strength == 0:
        yield
        return
    def hook(_module, _inputs, output):
        h = output_tensor(output)
        v = vector.to(device=h.device, dtype=h.dtype)
        require(v.ndim == 1 and v.numel() == h.shape[-1], 'Vector dimension mismatch.')
        changed = h.clone()
        # Prefill last position, then each cached decode position. Do not modify prompt history.
        changed[:, -1, :] = changed[:, -1, :] + strength * v
        return (changed,) + output[1:] if isinstance(output, tuple) else changed
    handle = layer.register_forward_hook(hook)
    try:
        yield
    finally:
        handle.remove()


def extract(a):
    require(not Path(a.output).exists(), 'Output already exists.')
    data = validate_dataset(read_json(a.input), a.db, a.owner)
    identity = model_identity(a.model)
    torch, tok, model, runtime = load_model(a.model, a.dtype, a.device, a.cpu_threads)
    layer_ids = sorted(set(a.layers))
    require(layer_ids and all(0 <= l < len(model.model.layers) for l in layer_ids),
            'Invalid layer index.')
    vectors = {l: [] for l in layer_ids}
    # Equal document-family weight: many chunks of one document cannot dominate.
    pairs = [p for p in data['pairs'] if p['split'] == 'train']
    with torch.inference_mode():
        for pair in pairs:
            activations = []
            for key in ('original', 'neutral'):
                text = extraction_text(pair[key], a.text_normalization)
                ids = tok(text, return_tensors='pt', add_special_tokens=False)['input_ids']
                require(ids.shape[1] > 0, 'Empty extraction text.')
                require(ids.shape[1] <= a.max_tokens,
                        f"{pair['pair_id']}: extraction text too long; do not silently truncate.")
                collected, handles = {}, []
                def capture(l):
                    def hook(_module, _inputs, output):
                        collected[l] = output_tensor(output)[0, -1].detach().float().cpu()
                    return hook
                try:
                    for l in layer_ids:
                        handles.append(model.model.layers[l].register_forward_hook(capture(l)))
                    model(input_ids=ids.to(a.device), use_cache=False)
                finally:
                    for handle in handles:
                        handle.remove()
                activations.append(collected)
            for l in layer_ids:
                vectors[l].append((pair['family_id'], activations[0][l] - activations[1][l]))
    output, diagnostics = {}, {}
    for l, values in vectors.items():
        families = sorted({f for f, _ in values})
        means = [torch.stack([v for f, v in values if f == family]).mean(0) for family in families]
        v = torch.stack(means).mean(0)
        norm = v.norm().item()
        require(math.isfinite(norm) and norm > 0, 'Degenerate or nonfinite style direction.')
        direction = v / norm
        output[str(l)] = direction.tolist()
        alignment = [torch.nn.functional.cosine_similarity(x[None], direction[None]).item()
                     for _, x in values if x.norm().item() > 0]
        diagnostics[str(l)] = {'raw_norm': norm, 'mean_alignment': sum(alignment) / len(alignment),
                               'pair_count': len(values), 'family_count': len(families)}
    write_new(a.output, {'format': 'voice-vector-v1', 'identity': identity, 'runtime': runtime,
                        'vectors': output, 'diagnostics': diagnostics,
                        'extraction': 'last-token narrative; equal family means; unit direction',
                        'text_normalization': a.text_normalization,
                        'dataset_sha256': data['dataset_sha256'], 'store_id': data['store_id'],
                        'corpus_revision': data['corpus_revision'],
                        'language': pairs[0]['language'], 'genre': pairs[0]['genre'],
                        'train_pairs': [p['pair_id'] for p in pairs],
                        'interpretation': 'Engineering pilot, not a reproduction or proof of disentanglement.'})


def generate(a):
    require(not Path(a.output).exists(), 'Output already exists.')
    vector_data = read_json(a.vector)
    require(vector_data.get('format') == 'voice-vector-v1', 'Invalid vector format.')
    current = validate_dataset(read_json(a.input), a.db, a.owner)
    for field in ('store_id', 'corpus_revision', 'dataset_sha256'):
        require(current[field] == vector_data[field], 'Voice evidence changed; re-extract the vector.')
    require(model_identity(a.model) == vector_data['identity'], 'Model/tokenizer snapshot mismatch.')
    torch, tok, model, runtime = load_model(a.model, a.dtype, a.device, a.cpu_threads)
    require(runtime == vector_data['runtime'], 'Runtime differs; re-extract and validate the vector.')
    key = str(a.layer)
    require(key in vector_data['vectors'], 'Layer was not extracted.')
    vector = torch.tensor(vector_data['vectors'][key], dtype=torch.float32)
    require(bool(torch.isfinite(vector).all()), 'Nonfinite vector.')
    tasks = read_json(a.tasks)
    require(isinstance(tasks, dict) and isinstance(tasks.get('tasks'), list) and tasks['tasks'],
            'Supply nonempty tasks.')
    strengths = a.strengths
    require(all(math.isfinite(x) for x in strengths) and 0 in strengths,
            'Include a zero-strength control and finite strengths.')
    rows = []
    if a.device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    with torch.inference_mode():
        for task in tasks['tasks']:
            require(task.get('language') == vector_data['language'] and
                    task.get('genre') == vector_data['genre'], 'Task language/genre mismatch.')
            prompt = tok.apply_chat_template(task['messages'], tokenize=False, add_generation_prompt=True)
            inputs = tok(prompt, return_tensors='pt', add_special_tokens=False).to(a.device)
            require(inputs['input_ids'].shape[1] <= a.max_tokens, 'Task prompt too long.')
            plain = None
            # An independent unhooked run verifies zero strength rather than trusting the label.
            for alpha in [None] + strengths:
                if a.device == 'cuda':
                    torch.cuda.synchronize()
                start = time.perf_counter()
                with intervention(model.model.layers[a.layer], vector, 0 if alpha is None else alpha):
                    ids = model.generate(**inputs, max_new_tokens=a.max_new_tokens, do_sample=False,
                                         use_cache=True, pad_token_id=tok.eos_token_id)
                if a.device == 'cuda':
                    torch.cuda.synchronize()
                generated = ids[0, inputs['input_ids'].shape[1]:].tolist()
                if alpha is None:
                    plain = generated
                    continue
                if alpha == 0:
                    require(generated == plain, 'Zero-strength output differs from unhooked baseline.')
                rows.append({'task_id': task['task_id'], 'strength': alpha, 'layer': a.layer,
                             'seconds': time.perf_counter() - start,
                             'max_new_tokens': a.max_new_tokens,
                             'finish_reason': finish_reason(generated, model.generation_config.eos_token_id,
                                                            a.max_new_tokens),
                             'text': tok.decode(generated, skip_special_tokens=True), 'token_ids': generated})
                print(f"Completed {task['task_id']} strength={alpha}, {len(generated)} tokens", flush=True)
    write_new(a.output, {'format': 'voice-generation-pilot-v1', 'runtime': runtime,
                        'model_sha256': vector_data['identity']['model_sha256'],
                        'vector_sha256': digest(vector_data), 'tasks_sha256': digest(tasks),
                        'zero_control_passed': True, 'rows': rows,
                        'peak_allocated_bytes': torch.cuda.max_memory_allocated() if a.device == 'cuda' else None,
                        'interpretation': 'Compare style and semantic quality separately; no automatic quality verdict.'})


def baseline(a):
    require(not Path(a.output).exists(), 'Output already exists.')
    identity = model_identity(a.model)
    torch, tok, model, runtime = load_model(a.model, a.dtype, a.device, a.cpu_threads)
    tasks = read_json(a.tasks)
    require(isinstance(tasks, dict) and isinstance(tasks.get('tasks'), list) and tasks['tasks'],
            'Supply nonempty tasks.')
    rows = []
    if a.device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    with torch.inference_mode():
        for task in tasks['tasks']:
            prompt = tok.apply_chat_template(task['messages'], tokenize=False, add_generation_prompt=True)
            inputs = tok(prompt, return_tensors='pt', add_special_tokens=False).to(a.device)
            require(inputs['input_ids'].shape[1] <= a.max_tokens, 'Task prompt too long.')
            if a.device == 'cuda':
                torch.cuda.synchronize()
            start = time.perf_counter()
            output = model.generate(**inputs, max_new_tokens=a.max_new_tokens, do_sample=False,
                                    use_cache=True, pad_token_id=tok.eos_token_id)
            if a.device == 'cuda':
                torch.cuda.synchronize()
            tokens = output[0, inputs['input_ids'].shape[1]:].tolist()
            rows.append({'task_id': task['task_id'], 'text': tok.decode(tokens, skip_special_tokens=True),
                         'token_ids': tokens, 'seconds': time.perf_counter() - start,
                         'finish_reason': finish_reason(tokens, model.generation_config.eos_token_id,
                                                        a.max_new_tokens)})
            print(f"Completed baseline {task['task_id']}, {len(tokens)} tokens", flush=True)
    write_new(a.output, {'format': 'voice-content-baseline-v1', 'identity': identity,
                        'runtime': runtime, 'tasks_sha256': digest(tasks), 'rows': rows,
                        'peak_allocated_bytes': torch.cuda.max_memory_allocated() if a.device == 'cuda' else None,
                        'interpretation': 'Unsteered content baseline; review semantics before comparing styles.'})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest='command', required=True)
    for name in ('extract', 'generate', 'baseline'):
        cmd = subs.add_parser(name)
        cmd.add_argument('--model', required=True)
        cmd.add_argument('--dtype', choices=['bfloat16', 'float32'], default='bfloat16')
        cmd.add_argument('--device', choices=['cpu', 'cuda'], default='cuda')
        cmd.add_argument('--max-tokens', type=int, default=1024)
        cmd.add_argument('--cpu-threads', type=int, default=1)
        cmd.add_argument('--output', required=True)
    e = subs.choices['extract']
    e.add_argument('--db', required=True); e.add_argument('--owner', required=True)
    e.add_argument('--input', required=True); e.add_argument('--layers', type=int, nargs='+', required=True)
    e.add_argument('--text-normalization', choices=['collapse-whitespace', 'strip', 'none'],
                   default='collapse-whitespace')
    g = subs.choices['generate']
    g.add_argument('--db', required=True); g.add_argument('--owner', required=True)
    g.add_argument('--input', required=True)
    g.add_argument('--vector', required=True); g.add_argument('--tasks', required=True)
    g.add_argument('--layer', type=int, required=True)
    g.add_argument('--strengths', type=float, nargs='+', default=[0, 0.5, 1.0])
    g.add_argument('--max-new-tokens', type=int, default=160)
    b = subs.choices['baseline']
    b.add_argument('--tasks', required=True)
    b.add_argument('--max-new-tokens', type=int, default=256)
    a = p.parse_args()
    {'extract': extract, 'generate': generate, 'baseline': baseline}[a.command](a)


if __name__ == '__main__':
    main()
