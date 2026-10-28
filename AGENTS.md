# URJAVYA POWER PRIVATE LIMITED

> Shared entry point for AI tools working in this repository. Keep project-wide agent guidance here and in the linked project documents. Tool-specific instruction files should point here instead of copying rules.

## Overview

- **Goal:** Build a corporate website and internal business system for URJAVYA POWER PRIVATE LIMITED.
- **Stack:** React, JavaScript, and Vite for the frontend; Node.js, JavaScript, Express, and REST APIs for the backend. The database is pending approval.
- **Status:** Documentation foundation; implementation has not started.

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
- Treat Pending, TBD, and Proposed items in project documents according to their stated status. Do not silently turn them into approved decisions.
- Before implementing a feature, read its relevant ticket and the applicable project specifications.

## Shared setup (how tools connect)

| Item | Location | Note |
|---|---|---|
| Shared agent entry point | `AGENTS.md` | Read this file first. Codex and tools that support the `AGENTS.md` convention can use it directly. |
| Project implementation rules | `docs/Rules.md` | Follow these rules along with the approved requirements and architecture documents. |
| Additional shared rules | `.agents/rules/` | Tool-neutral rules, one topic per file. |
| Shared hook implementations | `.agents/hooks/` | Reusable scripts; tool-specific hook configurations are adapters, not shared formats. |
| Claude Code pointer | `CLAUDE.md` | Imports this file. |
| Gemini / Antigravity pointer | `GEMINI.md` | Imports this file. |
| Cursor pointer | `.cursor/rules/main.mdc` | Always-on pointer to this file. |
| Other tools | `AGENTS.md` | Configure each tool to load this file where supported. |

**Rule for changes:**

- Add a new general agent rule once, in `AGENTS.md` or `.agents/rules/`.
- Never copy rules into tool-specific files.
- Put reusable hook logic in `.agents/hooks/`. Add only the minimal native configuration needed for a tool to call it.
- Hook events and configuration formats differ by tool. Do not claim a hook is active in a tool until its adapter is configured and tested.

## Project references

- Product requirements: `docs/PRD.md`
- Technical architecture and pending decisions: `docs/TECHNICAL_ARCHITECTURE.md`
- Implementation conventions: `docs/Rules.md`
- Frontend requirements: `docs/FRONTEND_SPECIFICATION.md`
- Security and access requirements: `docs/SECURITY_AND_ACCESS.md`
- Work phases: `docs/Phases.md`
- Feature tickets and their status: `docs/FEATURE_TICKETS.md`

## Guardrails

> To be defined. Will be added after discussion.

## Commands

> Add build, test, and run commands here once the stack is decided.

| Task | Command |
|---|---|
| Install | TBD |
| Run | TBD |
| Test | TBD |
| Lint | TBD |
