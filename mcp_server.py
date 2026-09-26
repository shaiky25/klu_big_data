#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp<2", "pyyaml"]
# ///
"""MCP server exposing this project's topics.yaml to Claude Desktop.

Reads topics.yaml live off disk on every call -- no upload, no sync
step. Reuses scripts/current_topic.py's parsing/mark_completed so both
the CLI and the MCP server share one source of truth.

Point Claude Desktop's config at this file (see README instructions
given alongside this file) and restart Desktop to pick it up.
"""
import importlib.util
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent
TOPICS_FILE = PROJECT_ROOT / "topics.yaml"
CURRENT_TOPIC_SCRIPT = PROJECT_ROOT / "skills/bda-weekly-deliverables/scripts/current_topic.py"


def _load_current_topic():
    spec = importlib.util.spec_from_file_location("current_topic", CURRENT_TOPIC_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ct = _load_current_topic()
mcp = FastMCP("bda-pop-topics")


@mcp.tool()
def list_sessions() -> list[dict]:
    """List every class session from topics.yaml: date, status, topics."""
    entries = ct.parse_entries(TOPICS_FILE.read_text())
    return [{"date": e["date"], "status": e["status"], "topics": e["topics"]} for e in entries]


@mcp.tool()
def current_topic(date: str | None = None) -> dict:
    """Resolve one week's topic. No date -> earliest pending entry (or
    latest if none pending). date, if given, is MM/DD/YYYY."""
    entries = ct.parse_entries(TOPICS_FILE.read_text())
    if date:
        idx = next((i for i, e in enumerate(entries) if e["date"] == date), None)
        if idx is None:
            raise ValueError(f"date {date} not found in {TOPICS_FILE}")
    else:
        idx = next((i for i, e in enumerate(entries) if e["status"] == "pending"), len(entries) - 1)
    e = entries[idx]
    session_number = idx + 1
    return {
        "date": e["date"],
        "status": e["status"],
        "topics": e["topics"],
        "topic_text": e["topic_text"],
        "session_number": session_number,
        "output_dir": f"session{session_number}",
    }


@mcp.tool()
def mark_topic_completed(date: str) -> dict:
    """Flip a session's status to completed in topics.yaml. date is MM/DD/YYYY."""
    entries = ct.parse_entries(TOPICS_FILE.read_text())
    idx = next((i for i, e in enumerate(entries) if e["date"] == date), None)
    if idx is None:
        raise ValueError(f"date {date} not found in {TOPICS_FILE}")
    ct.mark_completed(TOPICS_FILE, entries[idx]["date_iso"])
    return {"date": date, "status": "completed"}


if __name__ == "__main__":
    mcp.run()
