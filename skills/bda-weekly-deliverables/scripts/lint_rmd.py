#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Lint a weekly R Markdown deliverable against its hard, checkable
constraints: reproducible seed and zero external file dependencies.
Mirrors lint_deck.py's shape for the deck.

This is a text-level check, not a knit -- run it alongside (not instead
of) `Rscript -e 'rmarkdown::render("PATH.Rmd")'`.

Usage: lint_rmd.py PATH.Rmd
Exits 1 and prints one JSON object with an "issues" list (each entry
names the fix) if anything fails; exits 0 with {"ok": true} otherwise.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SEED_42 = re.compile(r"set\.seed\(\s*42\s*\)")
EXTERNAL_READ = re.compile(
    r"\b(read\.csv|read\.table|read_csv|read_excel|readRDS|read\.xlsx|source|load)\s*\("
)


def check_seed(text: str) -> list[str]:
    if not SEED_42.search(text):
        return ["no set.seed(42) found -- every week's Rmd must reproduce identically; add set.seed(42) before generating the dataset"]
    return []


def check_no_external_reads(text: str) -> list[str]:
    issues = []
    for m in EXTERNAL_READ.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        issues.append(
            f"line {line_no}: calls {m.group(1)}() -- the Rmd must stay self-contained for posit.cloud; "
            f"generate data in-place instead of reading or sourcing an external file"
        )
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rmd", help="path to the .Rmd to lint")
    args = ap.parse_args()

    path = Path(args.rmd)
    if not path.exists():
        print(json.dumps({"ok": False, "issues": [f"file not found: {path}"]}, indent=2))
        return 1

    text = path.read_text()
    issues = check_seed(text) + check_no_external_reads(text)

    print(json.dumps({"ok": not issues, "issues": issues}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
