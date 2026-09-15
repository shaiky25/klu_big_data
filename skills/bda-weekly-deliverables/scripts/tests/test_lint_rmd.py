#!/usr/bin/env python3
"""Tests for lint_rmd.py's hard-constraint checks.
Run with: uv run --with pytest -m pytest test_lint_rmd.py
(or plain `uv run test_lint_rmd.py` for a lightweight self-check).
"""
import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "lint_rmd.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("lint_rmd", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_clean_text_passes():
    mod = _load_module()
    text = "```{r}\nset.seed(42)\nx <- runif(10)\n```\n"
    assert mod.check_seed(text) == []
    assert mod.check_no_external_reads(text) == []


def test_missing_seed_is_caught():
    mod = _load_module()
    issues = mod.check_seed("```{r}\nx <- runif(10)\n```\n")
    assert len(issues) == 1


def test_wrong_seed_value_is_caught():
    mod = _load_module()
    issues = mod.check_seed("set.seed(1)\n")
    assert len(issues) == 1


def test_external_read_is_caught():
    mod = _load_module()
    issues = mod.check_no_external_reads('x <- read.csv("data.csv")\n')
    assert len(issues) == 1
    assert "read.csv" in issues[0]


def test_source_call_is_caught():
    mod = _load_module()
    issues = mod.check_no_external_reads('source("helpers.R")\n')
    assert len(issues) == 1


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    sys.exit(1 if failures else 0)
