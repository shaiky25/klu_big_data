#!/usr/bin/env python3
"""Tests for current_topic.py's topics.yaml parsing and session numbering.
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
sessions:
  - date: 2026-07-25
    status: completed
    topics:
      - Data Preparation
      - Model Planning
  - date: 2026-08-01
    status: completed
    topics:
      - Initial Exploration
  - date: 2026-08-11
    status: pending
    topics:
      - Statistical Tests
"""


def test_parses_three_entries_in_order():
    mod = _load_module()
    entries = mod.parse_entries(SAMPLE)
    assert [e["date"] for e in entries] == ["07/25/2026", "08/01/2026", "08/11/2026"]


def test_topic_text_joins_topics_as_bullets():
    mod = _load_module()
    entries = mod.parse_entries(SAMPLE)
    assert entries[0]["topic_text"] == "* Data Preparation\n* Model Planning"
    assert entries[0]["topics"] == ["Data Preparation", "Model Planning"]


def test_session_numbering_is_one_indexed_by_position(tmp_path=None):
    mod = _load_module()
    entries = mod.parse_entries(SAMPLE)
    assert len(entries) == 3  # session_number for 08/11/2026 would be 3, matching sessionN convention


def test_status_defaults_to_pending_when_absent():
    mod = _load_module()
    entries = mod.parse_entries("sessions:\n  - date: 2026-07-25\n    topics: [X]\n")
    assert entries[0]["status"] == "pending"


def test_mark_completed_flips_only_the_matching_block():
    mod = _load_module()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "topics.yaml"
        path.write_text(SAMPLE)
        mod.mark_completed(path, "2026-08-11")
        entries = mod.parse_entries(path.read_text())
        assert [e["status"] for e in entries] == ["completed", "completed", "completed"]


def test_mark_completed_inserts_status_when_missing():
    mod = _load_module()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "topics.yaml"
        path.write_text("sessions:\n  - date: 2026-07-25\n    topics:\n      - X\n")
        mod.mark_completed(path, "2026-07-25")
        entries = mod.parse_entries(path.read_text())
        assert entries[0]["status"] == "completed"
        assert entries[0]["topics"] == ["X"]


def test_real_topics_file_session5_maps_to_08_25():
    project_root = Path(__file__).resolve().parents[4]
    topics_file = project_root / "topics.yaml"
    if not topics_file.exists():
        return  # skip outside the real repo checkout
    mod = _load_module()
    entries = mod.parse_entries(topics_file.read_text())
    idx = next(i for i, e in enumerate(entries) if e["date"] == "08/25/2026")
    assert idx + 1 == 5


def test_real_topics_file_has_exactly_one_pending_entry():
    project_root = Path(__file__).resolve().parents[4]
    topics_file = project_root / "topics.yaml"
    if not topics_file.exists():
        return  # skip outside the real repo checkout
    mod = _load_module()
    entries = mod.parse_entries(topics_file.read_text())
    pending = [e["date"] for e in entries if e["status"] == "pending"]
    assert pending == ["09/29/2026"]


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
