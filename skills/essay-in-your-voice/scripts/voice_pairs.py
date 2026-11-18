"""Validate private, content-reviewed style pairs against the original voice store."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sqlite3


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def numbers(text):
    return Counter(re.findall(r'(?<![\w.])[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?%?(?!\w)', text))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def validate_pair_evidence(pair):
    """Check traceability, not the truth of the recorded semantic judgments."""
    pid = pair.get('pair_id', '?')
    evidence = pair.get('pair_evidence')
    require(isinstance(evidence, dict), f'{pid}: pair evidence is missing.')
    original, neutral = pair['original'], pair['neutral']
    require(evidence.get('original_sha256') == text_hash(original),
            f'{pid}: evidence bound to a different original.')
    require(evidence.get('neutral_sha256') == text_hash(neutral),
            f'{pid}: evidence bound to a different rewrite.')
    generation = evidence.get('generation', {})
    require(isinstance(generation, dict), f'{pid}: invalid generation record.')
    for key in ('model', 'created_at', 'method', 'prompt', 'raw_response'):
        require(isinstance(generation.get(key), str) and generation[key].strip(),
                f'{pid}: generation {key} is missing.')
    require(generation.get('model_id_status') in {'known', 'not_exposed'},
            f'{pid}: record whether the model identifier is exposed.')
    # A local editorial fix is replayed explicitly; the generated response stays intact.
    replay = generation['raw_response']
    edits = generation.get('edits', [])
    require(isinstance(edits, list), f'{pid}: invalid rewrite edits.')
    for edit in edits:
        require(isinstance(edit, dict) and isinstance(edit.get('before'), str)
                and edit['before'] and isinstance(edit.get('after'), str)
                and isinstance(edit.get('reason'), str) and edit['reason'].strip(),
                f'{pid}: rewrite edit needs exact text and reason.')
        require(replay.count(edit['before']) == 1,
                f'{pid}: rewrite edit must match exactly once.')
        replay = replay.replace(edit['before'], edit['after'], 1)
    require(replay == neutral, f'{pid}: generated response and edits do not reproduce rewrite.')
    require(isinstance(evidence.get('reviewer'), str) and evidence['reviewer'].strip(),
            f'{pid}: evidence reviewer is missing.')
    alignment = evidence.get('alignment')
    require(isinstance(alignment, list) and alignment, f'{pid}: claim alignment is missing.')
    covered = set()
    for row in alignment:
        require(isinstance(row, dict), f'{pid}: invalid alignment row.')
        index = row.get('claim_index')
        require(type(index) is int and 0 <= index < len(pair['content_contract']),
                f'{pid}: invalid claim index.')
        for key, text in (('original_quote', original), ('neutral_quote', neutral)):
            require(isinstance(row.get(key), str) and row[key].strip() and row[key] in text,
                    f'{pid}: {key} must be an exact nonempty anchor.')
        require(row.get('status') == 'pass' and isinstance(row.get('reason'), str)
                and row['reason'].strip(), f'{pid}: claim alignment needs a passing review.')
        covered.add(index)
    require(covered == set(range(len(pair['content_contract']))),
            f'{pid}: some content claims have no aligned evidence.')
    additions = evidence.get('addition_review', {})
    require(isinstance(additions, dict) and additions.get('status') == 'pass'
            and isinstance(additions.get('reason'), str) and additions['reason'].strip(),
            f'{pid}: review the rewrite for added claims.')


def validate_dataset(data, db_path, owner, require_pair_evidence=False):
    require(isinstance(data, dict) and isinstance(data.get('pairs'), list) and data['pairs'],
            'Supply a nonempty pairs list.')
    require(isinstance(owner, str) and owner.strip(), 'Supply an owner.')
    db_path = Path(db_path).resolve()
    require(db_path.is_file(), 'Original voice database is missing.')
    db = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        meta = dict(db.execute('SELECT key,value FROM meta'))
        require(meta.get('owner_id') == owner, 'Voice-store owner mismatch.')
        family_split, snapshot_split, content_split, seen = {}, {}, {}, set()
        result = []
        for pair in data['pairs']:
            require(isinstance(pair, dict), 'Each pair must be an object.')
            pid = pair.get('pair_id')
            require(isinstance(pid, str) and pid.strip() and pid not in seen,
                    'Pair IDs must be nonempty and unique.')
            seen.add(pid)
            source = db.execute('SELECT * FROM sources WHERE source_id=?',
                                (pair.get('source_id'),)).fetchone()
            require(source is not None, f'{pid}: source not found.')
            require(source['role'] == 'original' and source['authorship'] == 'confirmed',
                    f'{pid}: only confirmed originals are eligible.')
            split = pair.get('split')
            require(split in {'train', 'validation', 'test'}, f'{pid}: invalid split.')
            require(not source['holdout'] or split == 'test', f'{pid}: holdout is test-only.')
            start, end = pair.get('start'), pair.get('end')
            require(type(start) is int and type(end) is int and
                    0 <= start < end <= len(source['text']), f'{pid}: invalid original offsets.')
            original = source['text'][start:end]
            require(pair.get('original') == original, f'{pid}: original snapshot mismatch.')
            eligible = db.execute('SELECT 1 FROM chunks WHERE source_id=? AND start<=? AND end>=?',
                                  (source['source_id'], start, end)).fetchone()
            require(eligible is not None, f'{pid}: outside selected original narrative.')
            require(pair.get('source_sha256') == source['snapshot_sha256'],
                    f'{pid}: stale source snapshot.')
            neutral = pair.get('neutral')
            require(isinstance(neutral, str) and neutral.strip() and neutral != original,
                    f'{pid}: provide a distinct neutral text.')
            require(numbers(original) == numbers(neutral), f'{pid}: numerical content changed.')
            claims = pair.get('content_contract')
            require(isinstance(claims, list) and claims and
                    all(isinstance(c, str) and c.strip() for c in claims),
                    f'{pid}: content contract is missing.')
            literals = pair.get('protected_literals', [])
            require(isinstance(literals, list) and all(isinstance(x, str) and x for x in literals),
                    f'{pid}: invalid protected literals.')
            for literal in literals:
                require(original.count(literal) == neutral.count(literal) > 0,
                        f'{pid}: protected literal changed: {literal}')
            review = pair.get('review', {})
            require(isinstance(review, dict), f'{pid}: invalid review.')
            for key in ('facts', 'conditions', 'causality', 'stance'):
                check = review.get(key, {})
                require(isinstance(check, dict) and check.get('status') == 'pass' and
                        isinstance(check.get('reason'), str) and check['reason'].strip(),
                        f'{pid}: {key} needs an explicit semantic review.')
            if require_pair_evidence or 'pair_evidence' in pair:
                validate_pair_evidence(pair)
            require(isinstance(pair.get('topic'), str) and pair['topic'].strip(),
                    f'{pid}: topic label is missing.')
            for mapping, key, label in (
                    (family_split, source['family_id'], 'document family'),
                    (snapshot_split, source['snapshot_sha256'], 'source snapshot')):
                require(key not in mapping or mapping[key] == split,
                        f'{pid}: {label} leaks across splits.')
                mapping[key] = split
            for text in (original, neutral):
                key = digest(' '.join(text.casefold().split()))
                require(key not in content_split or content_split[key] == split,
                        f'{pid}: duplicate pair text leaks across splits.')
                content_split[key] = split
            result.append({**pair, 'family_id': source['family_id'],
                           'language': source['language'], 'genre': source['genre'],
                           'holdout': bool(source['holdout'])})
        require(len({(p['language'], p['genre']) for p in result}) == 1,
                'Build separate datasets for each language and genre.')
        counts = {s: sum(p['split'] == s for p in result)
                  for s in ('train', 'validation', 'test')}
        require(all(counts.values()), 'Include distinct train, validation and test families.')
        return {'format': 'voice-pairs-v1', 'owner': owner,
                'store_id': meta['store_id'], 'corpus_revision': int(meta['corpus_revision']),
                'pairs': result, 'counts': counts, 'families': len(family_split),
                'pairs_with_evidence': sum('pair_evidence' in p for p in result),
                'dataset_sha256': digest(result),
                'interpretation': 'Provenance and split checks passed. Semantic checks are agent judgments; no pure-style or sufficient-sample claim.'}
    finally:
        db.close()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', required=True)
    p.add_argument('--owner', required=True)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--require-pair-evidence', action='store_true',
                   help='Require replayable rewrite provenance and exact claim anchors.')
    a = p.parse_args()
    result = validate_dataset(read_json(a.input), a.db, a.owner, a.require_pair_evidence)
    write_new(a.output, result)
    print(json.dumps({k: result[k] for k in ('counts', 'families', 'dataset_sha256')}))


if __name__ == '__main__':
    main()
