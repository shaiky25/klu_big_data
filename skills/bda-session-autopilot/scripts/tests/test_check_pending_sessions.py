#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Unit tests for check-pending-sessions.py. Run: uv run scripts/tests/test_check_pending_sessions.py"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "check-pending-sessions.py"

TOPICS = """07/25/2026
* Old topic, never built

08/01/2026
* Built and unchanged

08/08/2026
* Built then edited
"""


def run(project_root: Path, *extra_args: str) -> tuple[int, dict | None, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(project_root), *extra_args],
        capture_output=True, text=True,
    )
    try:
        return result.returncode, json.loads(result.stdout), result.stderr
    except json.JSONDecodeError:
        return result.returncode, None, result.stderr


class CheckPendingSessions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "topics.txt").write_text(TOPICS)
        # session2 built and current; session3 built but topics.txt has since changed
        (self.root / "session2").mkdir()
        (self.root / "session3").mkdir()
        state_dir = self.root / "_bmad" / "memory" / "bda-session-autopilot"
        state_dir.mkdir(parents=True)
        (state_dir / "build-state.json").write_text(json.dumps({
            "session2": {"topic_text": "* Built and unchanged"},
            "session3": {"topic_text": "* Built then edited (old wording)"},
        }))

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_scope_is_latest_entry_only(self):
        code, data, _ = run(self.root)
        self.assertEqual(code, 0)
        total = len(data["pending"]) + len(data["changed"]) + len(data["current"])
        self.assertEqual(total, 1, "default run must only ever evaluate the latest entry")

    def test_latest_entry_flagged_changed_when_state_disagrees(self):
        _, data, _ = run(self.root)
        self.assertEqual(len(data["changed"]), 1)
        self.assertEqual(data["changed"][0]["session_number"], 3)

    def test_all_flag_buckets_every_entry(self):
        code, data, _ = run(self.root, "--all")
        self.assertEqual(code, 0)
        total = len(data["pending"]) + len(data["changed"]) + len(data["current"])
        self.assertEqual(total, 3)

    def test_all_flag_separates_pending_changed_current(self):
        _, data, _ = run(self.root, "--all")
        self.assertEqual([e["session_number"] for e in data["pending"]], [1])
        self.assertEqual([e["session_number"] for e in data["changed"]], [3])
        self.assertEqual([e["session_number"] for e in data["current"]], [2])

    def test_missing_topics_file_exits_2(self):
        (self.root / "topics.txt").unlink()
        code, data, stderr = run(self.root)
        self.assertEqual(code, 2)
        self.assertIsNone(data)
        self.assertIn("not found", stderr)


if __name__ == "__main__":
    unittest.main()
