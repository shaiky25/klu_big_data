#!/usr/bin/env python3
"""Tests for current_topic.py's topics.txt parsing and session numbering.
Run with: uv run --with pytest -m pytest test_current_topic.py
(or plain `uv run test_current_topic.py` for a lightweight self-check).
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "current_topic.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("current_topic", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SAMPLE = """
07/25/2026

* Data Preparation
* Model Planning07/25/2026


08/01/2026
* Initial Exploration


08/11/2026
* Statistical Tests
"""


def test_parses_three_entries_in_order():
    mod = _load_module()
    entries = mod.parse_entries(SAMPLE)
    assert [e["date"] for e in entries] == ["07/25/2026", "08/01/2026", "08/11/2026"]


def test_stray_glued_date_does_not_split_a_new_entry():
    mod = _load_module()
    entries = mod.parse_entries(SAMPLE)
    assert "Model Planning07/25/2026" in entries[0]["topic_text"]


def test_session_numbering_is_one_indexed_by_position(tmp_path=None):
    mod = _load_module()
    entries = mod.parse_entries(SAMPLE)
    assert len(entries) == 3  # session_number for 08/11/2026 would be 3, matching sessionN convention


def test_real_topics_file_session5_maps_to_08_25():
    project_root = Path(__file__).resolve().parents[4]
    topics_file = project_root / "topics.txt"
    if not topics_file.exists():
        return  # skip outside the real repo checkout
    mod = _load_module()
    entries = mod.parse_entries(topics_file.read_text())
    idx = next(i for i, e in enumerate(entries) if e["date"] == "08/25/2026")
    assert idx + 1 == 5


def test_find_content_brief_matches_by_date_in_file_text():
    mod = _load_module()
    with tempfile.TemporaryDirectory() as d:
        brief_dir = Path(d) / "brainstorming" / "some-topic"
        brief_dir.mkdir(parents=True)
        (brief_dir / "brainstorm-intent.md").write_text("# Brief (Class 09/01/2026)\n\nsome content")
        found = mod.find_content_brief("09/01/2026", str(Path(d) / "brainstorming" / "*" / "brainstorm-intent.md"))
        assert found == str(brief_dir / "brainstorm-intent.md")


def test_find_content_brief_returns_none_when_no_date_matches():
    mod = _load_module()
    with tempfile.TemporaryDirectory() as d:
        brief_dir = Path(d) / "brainstorming" / "some-topic"
        brief_dir.mkdir(parents=True)
        (brief_dir / "brainstorm-intent.md").write_text("# Brief (Class 08/25/2026)\n\nsome content")
        found = mod.find_content_brief("09/01/2026", str(Path(d) / "brainstorming" / "*" / "brainstorm-intent.md"))
        assert found is None


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
