"""Verify exact text edits against authorized highlight spans; preserve UTF-8 text."""

import argparse
import hashlib
import json
from pathlib import Path


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def bounds(item, length, allow_empty=False):
    start, end = item.get('start'), item.get('end')
    if type(start) is not int or type(end) is not int:
        raise ValueError('Offsets must be integer Unicode-code-point positions.')
    if not (0 <= start <= end <= length) or (start == end and not allow_empty):
        raise ValueError('A span is empty or outside the exact source snapshot.')
    return start, end


def verify(before, after, manifest):
    try:
        if not isinstance(manifest, dict):
            raise ValueError('Manifest must be an object.')
        if manifest.get('before_sha256', digest(before)) != digest(before):
            raise ValueError('Source hash does not match the manifest.')
        allowed = manifest.get('allowed_spans')
        edits = manifest.get('edits')
        if not isinstance(allowed, list) or not isinstance(edits, list):
            raise ValueError('Manifest needs allowed_spans and edits lists.')
        permitted = []
        for span in allowed:
            if not isinstance(span, dict):
                raise ValueError('Allowed spans must be objects.')
            start, end = bounds(span, len(before))
            if span.get('original') != before[start:end]:
                raise ValueError('An allowed-span source anchor does not match.')
            permitted.append((start, end))
        prepared = []
        for edit in edits:
            if not isinstance(edit, dict):
                raise ValueError('Edits must be objects.')
            start, end = bounds(edit, len(before), allow_empty=True)
            if edit.get('before') != before[start:end] or not isinstance(edit.get('after'), str):
                raise ValueError('An edit anchor or replacement is invalid.')
            if start == end:
                authorized = any(a < start < b for a, b in permitted)
            else:
                authorized = any(a <= start and end <= b for a, b in permitted)
            if not authorized:
                raise ValueError('An edit extends outside the authorized highlight scope.')
            prepared.append((start, end, edit['after']))
        prepared.sort(key=lambda item: (item[0], item[1]))
        previous = None
        for start, end, _ in prepared:
            if previous is not None:
                prev_start, prev_end = previous
                if start < prev_end or (start == prev_start and (start == end or prev_start == prev_end)):
                    raise ValueError('Edits overlap or insert ambiguously at the same position.')
            previous = (start, end)
        pieces, cursor = [], 0
        for start, end, replacement in prepared:
            pieces.extend((before[cursor:start], replacement))
            cursor = end
        pieces.append(before[cursor:])
        expected = ''.join(pieces)
        if expected != after:
            raise ValueError('Candidate differs from the exact permitted reconstruction; protected text changed or an edit is missing.')
        return {
            'ok': True, 'edit_count': len(prepared),
            'allowed_span_count': len(permitted),
            'protected_text_preserved': True,
            'before_sha256': digest(before), 'after_sha256': digest(after),
            'scope_only': 'Meaning, factual accuracy, author fit and detector outcomes require separate review.',
        }
    except ValueError as exc:
        return {'ok': False, 'protected_text_preserved': False, 'error': str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('before', 'after', 'manifest', 'output'):
        parser.add_argument('--' + option, required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve() in {args.before.resolve(), args.after.resolve(), args.manifest.resolve()}:
        parser.error('Output must be separate from all inputs.')
    if args.output.exists():
        parser.error('Choose a new output path to preserve the prior check.')
    try:
        before = args.before.read_bytes().decode('utf-8')
        after = args.after.read_bytes().decode('utf-8')
        manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
        result = verify(before, after, manifest)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print('Scope check passed.' if result['ok'] else 'Scope check failed; inspect the local result.')
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
