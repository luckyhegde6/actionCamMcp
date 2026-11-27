---
name: chatgpt-codex-github-workflow
description: Use ChatGPT Codex with GitHub repositories to inspect, edit, test, commit, push, and open pull requests safely. Distinguishes read-only ChatGPT GitHub access from Codex write workflows.
---

# ChatGPT Codex + GitHub Workflow

Use this skill when the user wants ChatGPT or Codex to work on a GitHub repository, including documentation, code changes, pull requests, reviews, or a GitHub Wiki.

## 1. Understand which GitHub integration is in use

Do not treat every GitHub connection in ChatGPT as having the same permissions.

- **GitHub app/connector in ChatGPT for repository Q&A:** OpenAI's GitHub connection article describes this surface as read access for searching, analyzing and citing repository content. It does not itself push code.
- **Codex:** Use Codex when the task requires editing files, running tests, committing, pushing or opening a pull request. Actual capabilities depend on the connected GitHub account, repository authorization, environment and user permissions.
- **GitHub MCP/connector tools:** Some ChatGPT environments expose additional read/write GitHub actions. Inspect the available action schema and permissions instead of assuming a connector is read-only or write-enabled.
- **Codex Cloud:** Runs in a remote, isolated task workspace. It can check out an authorized GitHub repository, edit files, run commands, and let the user review, commit or open a PR.
- **Codex Local/Worktree:** Works against a local project or isolated Git worktree in the ChatGPT desktop app. The app provides Git diff, staging, commit, push and PR actions.

## 2. Connect GitHub

1. Open ChatGPT Settings and find the GitHub app/connector under the available apps or plugins.
2. Start the GitHub authorization flow.
3. In GitHub, install/authorize the ChatGPT app and select the repositories it may access.
4. For an organization repository, request administrator approval if required.
5. Wait for a newly authorized repository to appear; OpenAI notes it can take several minutes.
6. Confirm the exact repository and account before beginning. A repository being visible does not grant write permission to Codex or a different connector.

OpenAI's GitHub connection setup and repository-selection instructions are in the official reference links below. Product UI labels can change; use current Settings labels.

## 3. Use Codex Cloud for remote repository work

1. In ChatGPT web or desktop, start a Codex/Work task and choose **Work in → Cloud**.
2. Select an available environment. If needed, create one and choose the authorized GitHub repository.
3. Let Codex inspect the repository and prepare its runtime/dependencies.
4. Review setup commands, access settings and test results. Publish a reusable environment only when its setup is ready.
5. Start a task with an explicit scope, for example:

   ```text
   Inspect the current repository state and existing documentation before editing.
   Work on a new branch based on the latest main.
   Update only the specified documentation and assets.
   Preserve architecture and naming conventions.
   Run markdown/link checks and the relevant tests.
   Show the diff and test evidence. Do not merge or deploy.
   ```

6. Inspect changed files, command output and test results.
7. Ask for fixes or review feedback in the same task.
8. When ready, use the Codex Git workflow to commit/push and open a PR, or ask Codex to prepare the PR for review.

Each cloud task has its own workspace. Local files, local browser sessions, local processes and VPN connections are not automatically available in the cloud. Upload or commit required assets into the repository, or use a supported cloud-accessible source.

## 4. Use Codex Local or Worktree

In the ChatGPT desktop app:
1. Choose Codex.
2. Select Local to work in the current checkout, or Worktree to isolate the task from the current checkout.
3. Open the repository folder.
4. Ask Codex to inspect the current branch, status, latest base branch and repository guidance before changes.
5. Make a small, scoped change and run project checks.
6. Review the diff pane; stage/revert individual files or hunks as needed.
7. Commit and push from the Git controls, then create a PR when appropriate.

The local environment's Git controls can stage, revert, commit, push a branch and create a pull request. Use the integrated terminal for Git operations not exposed in the UI.

## 5. Repository instructions and skills

Keep project-specific rules in `AGENTS.md` and reusable workflows in repository skills. For Codex, skills should follow the documented skill format and be stored in a supported skills location (for example, a repository's `.agents/skills/<skill-name>/SKILL.md` where supported). This repository also keeps human-readable workflow skill guides under `skills/`; copy or adapt them into the Codex-discovered skill directory if the selected client requires it.

A skill should include:
- YAML frontmatter with a concise `name` and `description`.
- Clear trigger conditions.
- Prerequisites and permissions.
- Step-by-step workflow.
- Safety boundaries and failure handling.
- Validation and reporting checklist.
- Official source links.

Do not assume that a `skills/` folder is automatically discovered by every Codex client. Check the selected client's current skill discovery documentation and project root.

## 6. GitHub Wiki is a separate Git repository

Do not try to update Wiki pages by writing `docs/wiki` or by assuming the main repository's Contents API covers the Wiki.

Use the companion [GitHub Wiki Git Publishing skill](../github-wiki-git-publishing/SKILL.md). The Wiki Git remote is `https://github.com/OWNER/REPO.wiki.git`; it may not exist until an initial Wiki page has been created in GitHub's Wiki UI.

For Wiki publishing, Codex needs:
- Network access to github.com.
- Git credentials with Wiki write permission.
- An initialized Wiki repository.
- A clean pull/rebase workflow that preserves existing Wiki pages.

## 7. Security and review rules

- Never paste tokens, passwords, private keys or API secrets into prompts or repository files.
- Use GitHub's authorization and Codex environment secret controls.
- Grant the minimum repository and environment permissions.
- Review every diff before commit/PR.
- Run the relevant tests and report exactly which checks ran.
- Never claim an unrun test passed.
- Do not merge, deploy, change repository settings or modify access controls unless the user explicitly requested it.
- Keep the user's requested branch/base branch and scope intact.
- If the connector is read-only or a repository is missing, explain the permission boundary and switch to Codex only if an authorized Codex environment is available.

## 8. Useful task prompts

### Inspect before changing
```text
Inspect this repository before making changes. Read AGENTS.md, README, relevant docs, recent commits and open PRs. Summarize the current implementation, constraints and smallest safe plan. Do not edit yet.
```

### Documentation-only PR
```text
Update the existing documentation without duplicating files. Verify every relative link and image path. Keep screenshots and diagrams as raster assets unless explicitly asked otherwise. Run markdown lint/link checks if configured. Create a branch and PR; do not merge.
```

### PR review
```text
Review this PR against its base branch. Prioritize correctness, regressions, missing tests, security and documentation drift. Do not change files. Cite exact file/line evidence and distinguish blockers from suggestions.
```

### Continue an existing task
```text
Continue the existing branch/task. First inspect Git status, current branch, latest remote base, commits and open PR. Preserve uncommitted work. Then implement only the remaining acceptance criteria and report validation evidence.
```

## Official references

- OpenAI Help — [Connecting GitHub to ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt)
- ChatGPT Learn — [Codex Cloud](https://learn.chatgpt.com/docs/cloud)
- ChatGPT Learn — [Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
- ChatGPT Learn — [Codex environments](https://learn.chatgpt.com/docs/environments/modes)
- ChatGPT Learn — [Local environments and built-in Git tools](https://learn.chatgpt.com/docs/environments/local-environment)
- ChatGPT Learn — [Review GitHub pull requests with Codex](https://learn.chatgpt.com/docs/third-party/github)
- ChatGPT Learn — [Codex GitHub Action](https://learn.chatgpt.com/docs/github-action)
- GitHub Docs — [GitHub Apps and repository permissions](https://docs.github.com/en/apps/using-github-apps/installing-a-github-app-from-a-third-party)
