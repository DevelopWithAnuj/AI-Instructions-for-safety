#!/usr/bin/env python3
"""Run: python3 .agents/hooks/selftest.py
Feeds sample tool calls to guard.py and checks block or allow."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "guard.py")


def bash(cmd):
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


def tool(name, **inp):
    return {"tool_name": name, "tool_input": inp}


CASES = [
    # (label, input, should_block)
    ("git push", bash("git push origin main"), True),
    ("git status", bash("git status"), True),
    ("gh cli", bash("gh pr create"), True),
    ("github mcp", tool("mcp__github__create_pull_request"), True),
    ("cursor style git", {"command": "git commit -m x"}, True),
    ("rm -rf", bash("rm -rf build"), True),
    ("find -delete", bash("find . -name '*.tmp' -delete"), True),
    ("python rmtree", bash("python3 -c 'import shutil; shutil.rmtree(\"x\")'"), True),
    ("psql", bash("psql -c 'select 1'"), True),
    ("drop table", bash("echo 'DROP TABLE users'"), True),
    ("db url", bash("curl postgres://u:p@host/db"), True),
    ("prisma migrate", bash("npx prisma migrate dev"), True),
    ("supabase mcp", tool("mcp__supabase__execute_sql"), True),
    ("sqlite file write", tool("Write", file_path="data.sqlite", content="x"), True),
    ("cd ..", bash("cd .."), True),
    ("read /etc", bash("cat /etc/passwd"), True),
    ("home dir", bash("cat ~/.ssh/id_rsa"), True),
    ("write outside", tool("Write", file_path="/tmp/x.txt", content="x"), True),
    ("read parent", tool("Read", file_path="../secret.txt"), True),
    ("bad json", "not json", True),
    ("ls", bash("ls -la"), False),
    ("cat inside", bash("cat README.md"), False),
    ("python print", bash("python3 -c 'print(1)'"), False),
    ("write inside", tool("Write", file_path="README.md", content="x"), False),
    ("docs mcp", tool("mcp__Claude_Docs__read"), False),
    ("devnull", bash("ls > /dev/null"), False),
]

fails = 0
for label, payload, should_block in CASES:
    data = payload if isinstance(payload, str) else json.dumps(payload)
    res = subprocess.run([sys.executable, GUARD], input=data, capture_output=True, text=True)
    blocked = res.returncode == 2
    ok = blocked == should_block
    fails += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + label + ("  (blocked)" if blocked else "  (allowed)"))

print("\n%d of %d passed" % (len(CASES) - fails, len(CASES)))
sys.exit(1 if fails else 0)
