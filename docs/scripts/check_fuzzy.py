#!/usr/bin/env python3
"""
Exit with status 1 if any non-obsolete PO entry is fuzzy, except the catalog header (msgid "").
"""

from __future__ import annotations

import sys
from pathlib import Path

import polib


def main() -> int:
    docs_dir = Path(__file__).resolve().parent.parent
    locale_dir = docs_dir / "locale"
    if not locale_dir.is_dir():
        return 0

    errors = 0
    for path in sorted(locale_dir.rglob("*.po")):
        rel = path.relative_to(docs_dir)
        po = polib.pofile(str(path), encoding="utf-8")
        for entry in po:
            if entry.obsolete:
                continue
            # Catalog header is the only normal empty msgid; it often stays #, fuzzy from Babel.
            if not entry.msgid:
                continue
            if not entry.fuzzy:
                continue
            preview = entry.msgid.replace("\n", "\\n")
            if len(preview) > 120:
                preview = preview[:117] + "..."
            print(f"{rel}: fuzzy message (msgid={preview!r})", file=sys.stderr)
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
