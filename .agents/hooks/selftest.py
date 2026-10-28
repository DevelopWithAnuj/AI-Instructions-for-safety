#!/usr/bin/env python3
"""Run: python3 .agents/hooks/selftest.py
Feeds sample tool calls through the guard and checks block or allow.
Network lock state is simulated, so the real .agents/ALLOW_NET file does not matter."""
import contextlib
import io
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import common  # noqa: E402
import check_net  # noqa: E402
import guard  # noqa: E402


def bash(cmd):
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


def tool(name, **inp):
    return {"tool_name": name, "tool_input": inp}


B, A = True, False  # expected: blocked, allowed

# (label, payload, expected, network_unlocked)
CASES = [
    # Phase 1: bypass tricks
    ("abs path git", bash("/usr/bin/git push"), B, False),
    ("sh -c git", bash('sh -c "git status"'), B, False),
    ("python -c", bash("python3 -c 'print(1)'"), B, False),
    ("node -e", bash("node -e 'console.log(1)'"), B, False),
    ("quote split rm", bash("r''m -rf x"), B, False),
    ("backslash rm", bash("r\\m -rf x"), B, False),
    ("command subst", bash("echo $(echo hi)"), B, False),
    ("backticks", bash("echo `ls`"), B, False),
    ("eval", bash("eval ls"), B, False),
    ("pipe to sh", bash("echo ls | sh"), B, False),
    ("base64 decode", bash("echo cm0= | base64 -d"), B, False),
    ("find -exec", bash("find . -exec ls {} ;"), B, False),
    ("xargs", bash("ls | xargs echo"), B, False),
    ("heredoc python", bash("python3 <<EOF\nprint(1)\nEOF"), B, False),
    ("symlink", bash("ln -s . x"), B, False),
    ("bad json", "not json", B, False),
    ("empty input", "", B, False),
    # Phase 2: git read-only
    ("git status", bash("git status"), A, False),
    ("git diff", bash("git diff"), A, False),
    ("git log", bash("git log --oneline"), A, False),
    ("git show", bash("git show HEAD"), A, False),
    ("git branch list", bash("git branch"), A, False),
    ("git branch -a", bash("git branch -a"), A, False),
    ("git branch create", bash("git branch newfeat"), B, False),
    ("git branch delete", bash("git branch -D x"), B, False),
    ("git add", bash("git add ."), B, False),
    ("git commit", bash("git commit -m x"), B, False),
    ("git push", bash("git push origin main"), B, False),
    ("git pull", bash("git pull"), B, False),
    ("git checkout", bash("git checkout main"), B, False),
    ("git reset", bash("git reset --hard"), B, False),
    ("git diff output", bash("git diff --output=x.txt"), B, False),
    ("git -c option", bash("git -c core.pager=x status"), B, False),
    ("git redirect", bash("git log > out.txt"), B, False),
    ("git chained", bash("git status && git push"), B, False),
    ("gh cli", bash("gh pr list"), B, False),
    ("github mcp", tool("mcp__github__list_issues"), B, False),
    ("cursor style git push", {"command": "git push"}, B, False),
    ("cursor style git status", {"command": "git status"}, A, False),
    # Phase 3: database (blocked even when network is unlocked)
    ("psql", bash("psql -c 'select 1'"), B, False),
    ("delete from", bash("echo 'DELETE FROM users'"), B, False),
    ("drop table", bash("echo 'DROP TABLE users'"), B, False),
    ("truncate", bash("echo 'TRUNCATE TABLE users'"), B, False),
    ("mongosh", bash("mongosh"), B, False),
    ("mongo deleteMany", bash("echo 'db.users.deleteMany({})'"), B, False),
    ("redis-cli", bash("redis-cli flushall"), B, False),
    ("redis flushall text", bash("echo flushall"), B, False),
    ("prisma migrate", bash("npx prisma migrate dev"), B, True),
    ("docker exec", bash("docker exec -it db bash"), B, True),
    ("compose exec", bash("docker compose exec db bash"), B, True),
    ("db url", bash("echo postgres://u:p@host/db"), B, True),
    ("supabase mcp", tool("mcp__supabase__execute_sql"), B, True),
    ("sqlite file write", tool("Write", file_path="data.sqlite", content="x"), B, False),
    # Phase 4: network closed
    ("curl", bash("curl https://example.com"), B, False),
    ("wget", bash("wget https://example.com"), B, False),
    ("ssh", bash("ssh host"), B, False),
    ("npm install", bash("npm install lodash"), B, False),
    ("pip install", bash("pip install requests"), B, False),
    ("npx", bash("npx create-react-app x"), B, False),
    ("WebFetch", tool("WebFetch", url="https://example.com"), B, False),
    ("WebSearch", tool("WebSearch", query="x"), B, False),
    ("Artifact", tool("Artifact", action="publish"), B, False),
    ("docs mcp locked", tool("mcp__Claude_Docs__read"), B, False),
    # Network unlocked by the user: these open, others stay closed
    ("curl unlocked", bash("curl https://example.com"), A, True),
    ("npm install unlocked", bash("npm install lodash"), A, True),
    ("WebFetch unlocked", tool("WebFetch", url="https://example.com"), A, True),
    ("docs mcp unlocked", tool("mcp__Claude_Docs__read"), A, True),
    ("git push unlocked", bash("git push"), B, True),
    ("github mcp unlocked", tool("mcp__github__create_pull_request"), B, True),
    ("agent makes ALLOW_NET", bash("touch .agents/ALLOW_NET"), B, True),
    ("agent writes ALLOW_NET", tool("Write", file_path=".agents/ALLOW_NET", content=""), B, True),
    # Delete
    ("rm -rf", bash("rm -rf build"), B, False),
    ("find -delete", bash("find . -name '*.tmp' -delete"), B, False),
    ("rmdir", bash("rmdir x"), B, False),
    # Scope
    ("cd ..", bash("cd .."), B, False),
    ("read /etc", bash("cat /etc/passwd"), B, False),
    ("home dir", bash("cat ~/.ssh/id_rsa"), B, False),
    ("write outside", tool("Write", file_path="/tmp/x.txt", content="x"), B, False),
    ("read parent", tool("Read", file_path="../secret.txt"), B, False),
    # Plain safe work
    ("ls", bash("ls -la"), A, False),
    ("cat inside", bash("cat README.md"), A, False),
    ("run selftest", bash("python3 .agents/hooks/selftest.py"), A, False),
    ("write inside", tool("Write", file_path="README.md", content="x"), A, False),
    ("devnull", bash("ls > /dev/null"), A, False),
]

SCRIPT_CASES = [
    ("script os.remove", "import os\nos.remove('x')", B),
    ("script rmtree", "import shutil\nshutil.rmtree('x')", B),
    ("script git push", "import os\nos.system('git push')", B),
    ("script DELETE FROM", "q = 'DELETE FROM users'", B),
    ("script plain", "print('hello')", A),
]


def run_case(payload, unlocked):
    data = payload if isinstance(payload, str) else json.dumps(payload)
    check_net.net_unlocked = lambda: unlocked
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            guard.run(common.parse(data))
    except SystemExit as exc:
        return exc.code == 2
    except Exception:
        return None  # crash inside the test, counts as a failure
    return False


def run_script(text):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            guard.scan_text(text)
    except SystemExit as exc:
        return exc.code == 2
    return False


fails = 0
total = 0


def report(label, expected, got):
    global fails, total
    total += 1
    ok = got is not None and got == expected
    fails += 0 if ok else 1
    state = "crash" if got is None else ("blocked" if got else "allowed")
    print(("PASS " if ok else "FAIL ") + label + "  (" + state + ")")


for label, payload, expected, unlocked in CASES:
    report(label, expected, run_case(payload, unlocked))

for label, text, expected in SCRIPT_CASES:
    report(label, expected, run_script(text))

# End to end through the real entry point (exit codes seen by the tools)
for label, data, expected in [
    ("e2e git push", json.dumps(bash("git push")), B),
    ("e2e bad json", "not json", B),
    ("e2e ls", json.dumps(bash("ls")), A),
]:
    res = subprocess.run([sys.executable, os.path.join(HERE, "guard.py")],
                         input=data, capture_output=True, text=True)
    report(label, expected, res.returncode == 2)

print("\n%d of %d passed" % (total - fails, total))
sys.exit(1 if fails else 0)
