# <PROJECT_NAME>

One-line description of the project.

## Getting started

1. Clone the repo.
2. Install dependencies (TBD).
3. Run the project (TBD).

## AI tools

This repository keeps shared agent guidance in one place. Claude Code, Gemini / Antigravity, Cursor, Codex, and other compatible tools should load the root `AGENTS.md` file.

- Read `AGENTS.md` first, then consult the project documents relevant to the task.
- Keep shared rules in `AGENTS.md` or `.agents/rules/`. Tool-specific files are pointers or minimal adapters only.
- Put reusable hook scripts in `.agents/hooks/`. Each tool needs its own native hook configuration, and some tools may not support the same events.
- No shared hook behavior is enabled yet. Add and test tool adapters when hook behavior is agreed.

## Structure

| Path | Purpose |
|---|---|
| `AGENTS.md` | Shared agent entry point and project references |
| `CLAUDE.md` | Claude Code pointer to `AGENTS.md` |
| `GEMINI.md` | Gemini / Antigravity pointer to `AGENTS.md` |
| `.cursor/rules/main.mdc` | Always-on Cursor pointer to `AGENTS.md` |
| `.claude/settings.json` | Claude Code's tool-specific settings and hook adapter configuration |
| `.agents/rules/` | Additional shared rules |
| `.agents/hooks/` | Reusable hook scripts and integration notes |
| `docs/` | Product, architecture, implementation, and feature specifications |

## Notes

- Repository files are written in English. Chat responses may use Hinglish.
- Project rules do not replace tool-native configuration. Each tool must be configured to load the shared entry point.
