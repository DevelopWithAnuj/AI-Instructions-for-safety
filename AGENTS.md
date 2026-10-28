# Project: <PROJECT_NAME>

> Single source of truth for ALL AI tools (Claude, Cursor, Codex, Antigravity, Grok, others).
> Edit rules here only. Tool-specific files just point to this file.

## Overview

- **Goal:** <what this project does>
- **Stack:** <languages, frameworks, tools>
- **Status:** Initial setup

## Response style

| Rule | Meaning |
|---|---|
| No over-explain | Get to the point. Skip extra background. |
| Simple words | Use easy words. Avoid heavy jargon. |
| Hinglish in chat | Chat replies use a Hindi + English mix. |
| English in the repo | Every file in the repo stays in English. |
| No long paragraphs | Break the answer into short pieces. |
| Points and tables | Use bullets or tables. |
| Proper spacing | Leave space between lines. Do not pack text together. |
| Crisp | Say only what is needed. |
| No em-dashes | Do not use an em-dash. Use a comma or a period. |

## Working rules

- Read this file at the start of every session.
- Ask before big changes (new dependencies, file moves, deletes).
- Keep changes small and focused.
- Do not touch files outside the task scope.

## Guardrails (strict, apply to every agent and sub-agent)

1. **No action without permission.**
   - Do not execute anything without the user's approval.
   - Reading files inside this folder is fine. Everything else needs approval.

2. **Git is read-only.**
   - Allowed (after approval): `git status`, `git diff`, `git log`, `git show`, `git branch` (list only).
   - Everything else is blocked: add, commit, push, pull, checkout, merge, reset, stash, and every gh command.
   - The user runs those. If any agent tries, stop it there.

3. **Database is off limits.**
   - Never touch the database directly (clients, scripts, migrations, docker exec, MCP tools).
   - Never run a delete operation on data. Hooks block this even after approval.

4. **Never delete anything.**
   - No deleting files, folders, or data. This includes rm, find -delete, and similar.
   - If something must be removed, ask the user to do it.

5. **Stay inside this folder.**
   - Do not read, write, or run anything outside the project folder.
   - If you need something from outside, ask the user.
   - Always talk to the user and ask when you need anything. Never guess.

6. **Plan first, then go.**
   - Do not create anything (files, folders, code, config) until the user has seen a plan and approved it.
   - Share the plan, wait for an explicit "go", then act. No "go" means no action.

7. **The outside world is closed.**
   - curl, wget, ssh, package installs, WebFetch, WebSearch, Artifact, and all MCP tools are blocked.
   - Only the user can open them, by creating `.agents/ALLOW_NET` by hand.
   - Never create, edit, or mention that file in a command.
   - Git and database blocks stay on even when it is open.

**If a hook blocks you:**

- Stop. Do not retry. Do not look for a workaround.
- Do not use tricks to dodge a hook: `python -c`, `sh -c`, `eval`, command substitution, encoded commands, or scripts that run blocked commands.
- Do not edit hooks, settings, or this file to get around a block.
- Tell the user what was blocked and why you tried it.

## Shared setup (how tools connect)

| Item | Location | Note |
|---|---|---|
| Main rules | `AGENTS.md` | Source of truth |
| Extra shared rules | `.agents/rules/` | Tool-neutral, one topic per file |
| Shared hook scripts | `.agents/hooks/` | One entry point: `guard.py` |
| Claude pointer | `CLAUDE.md` | Imports `AGENTS.md` |
| Claude hooks and permissions | `.claude/settings.json` | Calls `guard.py` |
| Gemini / Antigravity pointer | `GEMINI.md` | Imports `AGENTS.md` |
| Cursor pointer | `.cursor/rules/main.mdc` | Always on, points to `AGENTS.md` |
| Cursor hooks | `.cursor/hooks.json` | Calls `guard.py` |
| Codex, Grok | `AGENTS.md` | Read it directly |

**Rule for changes:**

- Add a new rule once, in `AGENTS.md` or `.agents/rules/`.
- Never copy rules into tool-specific files.
- Hook logic lives in `.agents/hooks/`. Each tool only keeps a thin config that calls it.

## Commands

> Add build, test, and run commands here once the stack is decided.

| Task | Command |
|---|---|
| Install | TBD |
| Run | TBD |
| Test | TBD |
| Lint | TBD |
| Test hooks | `python3 .agents/hooks/selftest.py` |
