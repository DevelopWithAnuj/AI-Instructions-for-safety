#!/usr/bin/env python3
"""Single entry point for all guardrail hooks.

Every tool config (Claude, Cursor, others) should call only this file:
    python3 .agents/hooks/guard.py

Reads the tool call as JSON on stdin. Exit code 2 blocks the action.
Any error also blocks (fail closed).
"""
import os
import re
import shlex
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

INTERP_NAME = re.compile(
    r"^(python[\d.]*|py|node|nodejs|deno|bun|perl|ruby|php|lua|bash|sh|zsh|dash|ksh|fish|pwsh)$")
MAX_SCRIPT = 1024 * 1024


def scan_text(text):
    """Check the text of a script the agent is about to run."""
    import common
    import check_git
    import check_delete
    import check_db
    for t in {text, common.normalize(text)}:
        check_git.check_text(t)
        check_delete.check({"command": t})
        check_db.check({"command": t, "tool": "", "paths": [], "is_mcp": False})


def _scan_file(target):
    import common
    from pathlib import Path
    p = Path(os.path.expanduser(target))
    if not p.is_absolute():
        p = common.ROOT / p
    p = p.resolve()
    root = common.ROOT
    if not (p == root or root in p.parents):
        return
    if not p.is_file() or p.stat().st_size > MAX_SCRIPT:
        return
    hooks = root / ".agents" / "hooks"
    if hooks in p.parents:
        return
    scan_text(p.read_text(errors="replace"))


def scan_scripts(ctx):
    """If the command runs a script file inside the project, check what is inside it."""
    import common
    for seg in common.segments(ctx["command"]):
        try:
            tokens = shlex.split(seg)
        except ValueError:
            continue
        while tokens and re.match(r"^\w+=", tokens[0]):
            tokens.pop(0)
        if not tokens:
            continue
        target = None
        if INTERP_NAME.match(os.path.basename(tokens[0]).lower()):
            for t in tokens[1:]:
                if not t.startswith("-"):
                    target = t
                    break
        elif "/" in tokens[0]:
            target = tokens[0]
        if target:
            _scan_file(target)


def run(ctx):
    import common
    import check_bypass
    import check_git
    import check_delete
    import check_db
    import check_net
    import check_scope

    raw = ctx["command"]
    variants = [raw]
    norm = common.normalize(raw)
    if norm != raw:
        variants.append(norm)
    for text in variants:
        c = dict(ctx)
        c["command"] = text
        for module in (check_bypass, check_git, check_delete, check_db, check_net):
            module.check(c)
    check_scope.check(ctx)
    scan_scripts(ctx)


def main():
    import common
    run(common.load())


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("BLOCKED by project guardrails: hook crashed (%s). Fail closed.\n" % exc)
        sys.exit(2)
