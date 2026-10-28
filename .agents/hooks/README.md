# Hooks

One entry point: `guard.py`. Every tool calls only this file.

| File | Guardrail | What it blocks |
|---|---|---|
| `check_bypass.py` | all | `python -c`, `sh -c`, `eval`, `$(...)`, backticks, heredoc scripts, pipe to shell, xargs, find -exec, ln, base64 decode |
| `check_git.py` | 2 | Everything except read-only git (status, diff, log, show, branch list). All gh, hub, glab, GitHub APIs and MCP tools |
| `check_db.py` | 3 | DB clients, migrations, DROP/DELETE/TRUNCATE, Mongo and Redis deletes, docker exec, DB URLs, DB MCP tools, DB files |
| `check_delete.py` | 4 | rm, rmdir, unlink, find -delete, rmtree and similar |
| `check_scope.py` | 5 | Any path outside the project folder (`..`, `~`, absolute paths) |
| `check_net.py` | 7 | curl, wget, ssh, package installs, npx, WebFetch, WebSearch, Artifact, all MCP tools |
| `common.py` | all | Reads input, blocks with exit code 2, fails closed |
| `guard.py` | all | Runs every check. Also reads script files the agent runs and checks what is inside |
| `selftest.py` | all | Test cases to confirm the hooks work |

Guardrails 1 and 6 (ask first, plan first) are enforced by tool settings
(see `.claude/settings.json`) and by `AGENTS.md`.

## Fail closed

- A crash inside the hook blocks the action.
- Empty or broken input blocks the action.
- In Claude settings the command ends with `|| exit 2`, so even a missing Python blocks.

## Network lock (`.agents/ALLOW_NET`)

- Locked by default. No file means closed.
- To open: the user creates an empty file `.agents/ALLOW_NET` by hand.
- To close: the user removes that file.
- Agents cannot create, edit or mention it. The hook blocks that.
- Git and database blocks stay on even when it is open.

## Known limits

- Checks are pattern based. A very clever disguise can still slip through. Keep the permission prompts on.
- Scripts are checked by their text only. `npm run`, `make` and indirect calls are not read.
- Tool hooks work only where a tool supports them (Claude: full, Cursor: shell, MCP and file read).

## Test

```
python3 .agents/hooks/selftest.py
```

## Adding a new check

1. Create `check_<name>.py` with a `check(ctx)` function.
2. Import it and add it to the loop in `guard.py`.
3. Add cases to `selftest.py`.

## Requirements

- Python 3 (standard library only, no installs).
