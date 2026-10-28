"""Shared helpers for guardrail hooks. Python 3, standard library only."""
import json
import re
import sys
from pathlib import Path

# Project root = two levels above this file (.agents/hooks/common.py)
ROOT = Path(__file__).resolve().parents[2]

SPLIT = re.compile(r"&&|\|\||[;|&\n]")


def block(reason):
    """Stop the action. Exit code 2 blocks the tool call in Claude Code and Cursor."""
    sys.stderr.write(
        "BLOCKED by project guardrails: " + reason + "\n"
        "Stop now. Do not retry or work around this. Tell the user and ask.\n"
    )
    sys.exit(2)


def normalize(cmd):
    """Remove quotes, backslashes and IFS tricks, so r''m or g\\it cannot hide a command."""
    cmd = re.sub(r"\$\{?IFS\}?", " ", cmd)
    return re.sub(r"[\\'\"]", "", cmd)


def segments(cmd):
    """Split a shell line into separate commands."""
    return [s.strip() for s in SPLIT.split(cmd) if s.strip()]


def parse(raw):
    """Turn the hook JSON text into a context dict. Fail closed if anything looks wrong."""
    if not raw or not raw.strip():
        block("hook got empty input (fail closed).")
    try:
        data = json.loads(raw)
    except ValueError:
        block("hook could not read its input (fail closed).")
    if not isinstance(data, dict):
        block("hook input has an unexpected shape (fail closed).")

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    tool = str(data.get("tool_name") or "")
    event = str(data.get("hook_event_name") or "")

    command = tool_input.get("command") or data.get("command") or ""
    if not isinstance(command, str):
        command = ""

    paths = []
    for src in (tool_input, data):
        for key in ("file_path", "path", "notebook_path", "filePath"):
            value = src.get(key)
            if isinstance(value, str) and value:
                paths.append(value)
    if tool == "Glob":
        pattern = tool_input.get("pattern")
        if isinstance(pattern, str) and pattern:
            paths.append(pattern)

    is_mcp = tool.lower().startswith("mcp") or event == "beforeMCPExecution"
    return {"tool": tool, "command": command, "paths": paths, "is_mcp": is_mcp}


def load():
    return parse(sys.stdin.read())
