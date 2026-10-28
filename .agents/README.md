# Shared agent resources

Shared, tool-neutral resources for AI tools used in this repository.

| Folder | Purpose |
|---|---|
| `rules/` | Additional shared rules, one topic per Markdown file |
| `hooks/` | Reusable hook scripts and notes on tool adapters |

## How to use

- Put general rules in the root `AGENTS.md` or add a focused rule here once. Do not copy shared rule text into tool-specific files.
- Put reusable hook logic in `hooks/`. Native tool configurations should stay small and call the shared implementation where supported.
- Hook configuration formats, event names, and support vary between tools. A shared script alone does not activate a hook in every tool.
- See `hooks/README.md` before adding hook behavior or a tool adapter.
