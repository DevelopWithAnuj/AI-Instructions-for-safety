#!/usr/bin/env python3
"""Single entry point for all guardrail hooks.

Every tool config (Claude, Cursor, others) should call only this file:
    python3 .agents/hooks/guard.py

Reads the tool call as JSON on stdin. Exit code 2 blocks the action.
Any error also blocks (fail closed).
"""
import os
import sys

sys.dont_write_bytecode = True


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import common
    import check_git
    import check_delete
    import check_db
    import check_scope

    ctx = common.load()
    for module in (check_git, check_delete, check_db, check_scope):
        module.check(ctx)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("BLOCKED by project guardrails: hook crashed (%s). Fail closed.\n" % exc)
        sys.exit(2)
