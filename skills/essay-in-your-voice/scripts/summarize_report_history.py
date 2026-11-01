"""Summarize private report observations without fitting or inventing an AI score."""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def score_bounds(score):
    if type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 100:
        return (score, score, True, True)
    if isinstance(score, dict) and score.get('state') == 'suppressed':
        threshold = score.get('below')
        if type(threshold) in (int, float) and math.isfinite(threshold) and 0 < threshold <= 100:
            return (0, threshold, False, False)
    raise ValueError('Scores must be numbers from 0 to 100 or a positive suppressed/below state.')


def consistent(scores):
    intervals = [score_bounds(s) for s in scores]
    lo = max(x[0] for x in intervals)
    hi = min(x[1] for x in intervals)
    if lo < hi:
        return True
    if lo > hi:
        return False
    return all((x[0] < lo or x[2]) and (x[1] > hi or x[3]) for x in intervals)


def summarize(data):
    reports = data.get('reports') if isinstance(data, dict) else data
    if not isinstance(reports, list) or not reports:
        raise ValueError('Provide a nonempty report list.')
    unique = {}
    families = set()
    fingerprints = defaultdict(list)
    numeric = []
    suppressed = 0
    for row in reports:
        if not isinstance(row, dict):
            raise ValueError('Each report must be an object.')
        for field in ('report_id', 'family_id', 'tool'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('Each report needs report_id, family_id and tool strings.')
        score_bounds(row.get('score'))
        for field in ('submission_id', 'prose_fingerprint'):
            if row.get(field) is not None and not isinstance(row[field], str):
                raise ValueError('Optional identifiers and fingerprints must be strings.')
        key = (row['tool'], row.get('submission_id') or row['report_id'])
        if key not in unique:
            unique[key] = []
        unique[key].append(row)
        families.add(row['family_id'])
    duplicate_conflicts = []
    for key, rows in unique.items():
        scores = []
        signatures = set()
        for row in rows:
            signature = json.dumps(row['score'], sort_keys=True)
            if signature not in signatures:
                signatures.add(signature)
                scores.append(row['score'])
        metadata = {(row['family_id'], row.get('prose_fingerprint'), row.get('submitted_file_sha256'), row.get('model_version')) for row in rows}
        if len(signatures) > 1 or len(metadata) > 1:
            duplicate_conflicts.append({'tool': key[0], 'submission_key': key[1], 'reason': 'Duplicate submission has differing score or identity metadata.'})
        for score in scores:
            if type(score) in (int, float):
                numeric.append(score)
            else:
                suppressed += 1
        # Conflicting duplicates stay visible but do not supply trusted prose comparisons.
        if len(metadata) == 1 and len(signatures) == 1:
            row = rows[0]
            fingerprint = row.get('prose_fingerprint')
            if fingerprint:
                fingerprints[(row['family_id'], fingerprint)].append(row)
    disagreements = []
    for (family, fingerprint), rows in fingerprints.items():
        scores = [row['score'] for row in rows]
        if len(rows) > 1 and not consistent(scores):
            disagreements.append({
                'family_id': family, 'prose_fingerprint': fingerprint,
                'observations': [{'report_id': row['report_id'], 'tool': row['tool'], 'model_version': row.get('model_version'), 'score': row['score']} for row in rows],
                'interpretation': 'Matching declared prose scope has incompatible score observations; submitted files and processing conditions may differ.',
            })
    return {
        'input_records': len(reports), 'unique_submissions': len(unique),
        'duplicate_records': len(reports) - len(unique),
        'independent_document_families': len(families),
        'numeric_observed_range': [min(numeric), max(numeric)] if numeric else None,
        'suppressed_score_observations': suppressed,
        'duplicate_metadata_conflicts': duplicate_conflicts,
        'same_prose_score_disagreements': disagreements,
        'prediction': None,
        'calibration_status': 'case_history_only' if len(families) == 1 else 'not_fitted',
        'interpretation': 'Observed score range is history, not a prediction interval. Reports within one document family are correlated.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve() == args.input.resolve() or args.output.exists():
        parser.error('Choose a new output path separate from the input.')
    try:
        result = summarize(json.loads(args.input.read_text(encoding='utf-8-sig')))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print('Saved private report-history summary.')


if __name__ == '__main__':
    main()
