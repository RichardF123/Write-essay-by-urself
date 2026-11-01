"""Compare UTF-8 drafts by blank-line paragraphs; no detector interpretation."""

import argparse
import hashlib
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


def read_draft(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "paragraph_count": len(paragraphs),
    }, paragraphs


def compare(before, after):
    before_meta, old = read_draft(before)
    after_meta, new = read_draft(after)
    blocks = []
    for kind, i, j, k, m in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        blocks.append({
            "operation": kind,
            "before_ids": [f"P{n + 1:02d}" for n in range(i, j)],
            "after_ids": [f"P{n + 1:02d}" for n in range(k, m)],
            "before_text": old[i:j],
            "after_text": new[k:m],
            "mapping": "exact block" if kind == "equal" else "manual alignment required",
        })
    return {
        "before": before_meta,
        "after": after_meta,
        "method": "Blank-line paragraphs, outer whitespace trimmed, line endings normalized; paragraph-internal text retained. IDs are version-local, not stable cross-version IDs.",
        "limitations": "No PDF color extraction, authorship judgment, automatic semantic mapping, or causal attribution. Output contains private draft text.",
        "blocks": blocks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve() in {args.before.resolve(), args.after.resolve()}:
        parser.error("Output must not overwrite either input draft.")
    if args.output.exists():
        parser.error("Output already exists; choose a new path to preserve prior analyses.")
    try:
        result = compare(args.before, args.after)
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(f"Saved version comparison to {args.output}")


if __name__ == "__main__":
    main()
