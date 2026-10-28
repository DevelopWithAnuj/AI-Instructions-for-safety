@AGENTS.md

## Claude-specific notes

- All shared rules are in `AGENTS.md` (imported above). Do not duplicate them here.
- Claude settings and hooks config live in `.claude/settings.json`.
- Reusable hook logic belongs in `.agents/hooks/`; configure and test Claude-specific hook adapters in `.claude/settings.json`.
