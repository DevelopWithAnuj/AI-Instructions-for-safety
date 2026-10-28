# <PROJECT_NAME>

<One-line description of the project.>

## Getting started

1. Clone the repo.
2. Install dependencies (TBD).
3. Run the project (TBD).

## AI tools

This repo works with Claude, Cursor, Codex, Antigravity, Grok and others.

- All shared rules are in `AGENTS.md`. This is the single source of truth.
- Tool-specific files only point to `AGENTS.md`. Do not copy rules into them.
- Shared rules and hook scripts live in `.agents/`.

## Guardrails

Every agent and sub-agent must follow these. Hooks enforce them.

| # | Guardrail |
|---|---|
| 1 | No action without the user's permission |
| 2 | Git is read-only (status, diff, log, show, branch list). No gh. The user runs the rest |
| 3 | No direct database access. No data deletes |
| 4 | No deleting files, folders, or data |
| 5 | Stay inside the project folder |
| 6 | Plan first. Create nothing until the user approves with "go" |
| 7 | Network and outside tools are closed. Only the user opens them with `.agents/ALLOW_NET` |

Test the hooks:

```
python3 .agents/hooks/selftest.py
```

## Folder structure

```
.
├── AGENTS.md                  # Source of truth for all AI tools
├── CLAUDE.md                  # Claude pointer (imports AGENTS.md)
├── GEMINI.md                  # Gemini and Antigravity pointer
├── README.md                  # This file
│
├── .claude/
│   └── settings.json          # Claude permissions and hooks wiring
│
├── .cursor/
│   ├── hooks.json             # Cursor hooks wiring
│   └── rules/
│       └── main.mdc           # Cursor pointer (always on)
│
└── .agents/                   # Shared, tool-neutral folder
    ├── README.md              # Guide for this folder
    ├── ALLOW_NET              # Optional. Only the user creates it to open the network
    ├── rules/                 # Extra shared rules (empty for now)
    └── hooks/
        ├── README.md          # Hooks guide
        ├── guard.py           # Single entry point for all tools
        ├── common.py          # Shared helpers, fail-closed blocking
        ├── check_bypass.py    # Blocks tricks to hide commands
        ├── check_git.py       # Allows read-only git, blocks the rest
        ├── check_db.py        # Blocks direct database access
        ├── check_delete.py    # Blocks deletes
        ├── check_net.py       # Blocks network, installs, web tools, MCP
        ├── check_scope.py     # Blocks paths outside the folder
        └── selftest.py        # Tests for the hooks
```

| Path | Purpose |
|---|---|
| `AGENTS.md` | Rules, response style, guardrails |
| `CLAUDE.md`, `GEMINI.md` | Pointer files, import `AGENTS.md` |
| `.claude/settings.json` | Claude permissions (plan mode, ask, deny) and hooks |
| `.cursor/` | Cursor rule pointer and hooks |
| `.agents/rules/` | Extra shared rules, one topic per file |
| `.agents/hooks/` | Guardrail scripts. Every tool calls `guard.py` |

## Notes

- All files in this repo are written in English.
- Chat replies from agents use Hinglish.
- Add new rules once, in `AGENTS.md` or `.agents/rules/`.
- Hooks need Python 3 (standard library only).
