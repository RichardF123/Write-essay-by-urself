"""Summarize verified highlight observations for one essay; no PDF reading or edit authorization."""

import argparse
import json
from pathlib import Path


STATES = {'full', 'partial', 'none', 'unknown'}
MAPPINGS = {'exact', 'rewrite', 'split', 'merge', 'uncertain'}


def required_string(row, key):
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{key} must be a nonempty string.')
    return value


def summarize(data, min_highlights=2):
    if type(min_highlights) is not int or min_highlights < 1:
        raise ValueError('min_highlights must be a positive integer.')
    if not isinstance(data, dict):
        raise ValueError('Provide an object with family_id, reports, latest_report_id and units.')
    family = required_string(data, 'family_id')
    reports, units = data.get('reports'), data.get('units')
    if not isinstance(reports, list) or not reports or not isinstance(units, list):
        raise ValueError('reports must be nonempty and units must be a list.')
    aliases, unique = {}, {}
    for row in reports:
        if not isinstance(row, dict):
            raise ValueError('Each report must be an object.')
        report_id = required_string(row, 'report_id')
        tool = required_string(row, 'tool')
        draft = required_string(row, 'draft_id')
        submission = row.get('submission_id')
        if submission is not None and (not isinstance(submission, str) or not submission.strip()):
            raise ValueError('submission_id must be a nonempty string when supplied.')
        if report_id in aliases:
            raise ValueError('report_id must be unique; use submission_id to identify duplicate downloads.')
        key = (tool, submission or report_id)
        if key in unique and unique[key]['draft_id'] != draft:
            raise ValueError('Duplicate submission maps to conflicting drafts.')
        unique.setdefault(key, row)
        aliases[report_id] = key
    latest_id = required_string(data, 'latest_report_id')
    if latest_id not in aliases:
        raise ValueError('latest_report_id must name a supplied report.')
    latest_key = aliases[latest_id]
    output = []
    seen_units = set()
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError('Each unit must be an object.')
        unit_id = required_string(unit, 'unit_id')
        if unit_id in seen_units:
            raise ValueError('unit_id must be unique.')
        seen_units.add(unit_id)
        observations = unit.get('observations')
        if not isinstance(observations, list):
            raise ValueError('observations must be a list.')
        by_submission = {}
        for row in observations:
            if not isinstance(row, dict):
                raise ValueError('Each observation must be an object.')
            report_id = required_string(row, 'report_id')
            if report_id not in aliases:
                raise ValueError('Observation references an unknown report.')
            state, mapping = row.get('highlight'), row.get('mapping')
            if state not in STATES or mapping not in MAPPINGS:
                raise ValueError('Invalid highlight or mapping state.')
            text = row.get('text')
            if text is not None and not isinstance(text, str):
                raise ValueError('Observation text must be a string.')
            if state != 'unknown':
                required_string(row, 'locator')
                required_string(row, 'text')
            signature = (state, mapping, text)
            key = aliases[report_id]
            if key in by_submission and by_submission[key] != signature:
                raise ValueError('Duplicate submission has conflicting unit observations.')
            by_submission[key] = signature
        # Missing or uncertain alignments cannot supply negative or positive labels.
        known = {k: v for k, v in by_submission.items() if v[0] != 'unknown' and v[1] != 'uncertain'}
        full = sum(v[0] == 'full' for v in known.values())
        partial = sum(v[0] == 'partial' for v in known.values())
        count = full + partial
        latest = known.get(latest_key)
        latest_state = latest[0] if latest else 'unknown'
        texts = [v[2] for v in known.values()]
        unchanged = len(texts) >= 2 and len(set(texts)) == 1
        complete = len(known) == len(unique)
        output.append({
            'unit_id': unit_id,
            'full_highlight_count': full,
            'partial_highlight_count': partial,
            'confirmed_highlight_count': count,
            'observed_submissions': len(known),
            'unknown_submissions': len(unique) - len(known),
            'at_least_requested_count': count >= min_highlights,
            'exactly_requested_count': count == min_highlights if complete else None,
            'same_text_across_observed_versions': unchanged,
            'latest_state': latest_state,
            'review_candidate': count >= min_highlights and latest_state in {'full', 'partial'},
            'current_edit_permission': 'not_determined',
        })
    return {
        'family_id': family, 'unique_submissions': len(unique),
        'duplicate_downloads': len(reports) - len(unique),
        'latest_report_id': latest_id, 'min_highlights': min_highlights,
        'units': output,
        'interpretation': 'Counts describe verified overlap, including partial highlights. Unknowns are not negatives. Review candidates are not editable spans or detector predictions.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--min-highlights', type=int, default=2)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error('Choose a new output path separate from the input.')
    try:
        result = summarize(json.loads(args.input.read_text(encoding='utf-8-sig')), args.min_highlights)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print('Saved private repeated-highlight summary.')


if __name__ == '__main__':
    main()
