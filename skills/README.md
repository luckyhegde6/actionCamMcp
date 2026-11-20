# Repository Skills

Reusable workflow guides for contributors and AI coding agents.

## Available skills

| Skill | Human-readable guide | Codex-discoverable copy |
|---|---|---|
| ChatGPT Codex + GitHub | [SKILL.md](chatgpt-codex-github-workflow/SKILL.md) | [SKILL.md](../.agents/skills/chatgpt-codex-github-workflow/SKILL.md) |
| GitHub Wiki Git Publishing | [SKILL.md](github-wiki-git-publishing/SKILL.md) | [SKILL.md](../.agents/skills/github-wiki-git-publishing/SKILL.md) |

The canonical human-readable guides live under `skills/`. Matching copies under `.agents/skills/<skill-name>/SKILL.md` follow the repository-level Codex skill discovery convention documented by OpenAI. Keep both copies synchronized when changing a workflow.

## Skill authoring rules

Each skill must include:
- YAML frontmatter with `name` and a concise `description`.
- Explicit trigger conditions.
- Prerequisites, repository and account permission requirements.
- A step-by-step workflow.
- Safety boundaries and failure handling.
- Validation and reporting checklists.
- Official documentation links.

Do not assume a generic `skills/` directory is automatically discovered by every Codex client. The supported discovery path depends on the client; this repository uses `.agents/skills/` for Codex project-level skills and `skills/` for human-readable source documentation.
