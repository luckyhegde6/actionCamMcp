# GitHub Wiki and ChatGPT Codex Publishing Workflow

This project uses two separate Git destinations:

1. **Normal repository** (`luckyhegde6/actionCamMcp`): canonical source for camera lessons, diagrams, project documentation and reusable agent guidance.
2. **GitHub Wiki** (`luckyhegde6/actionCamMcp.wiki.git`): reader-facing long-form Wiki pages and their image assets.

## Why the GitHub connector returned 404

The public Wiki pages are already published and accessible. The 404 occurs when the ChatGPT GitHub connector tries to resolve `luckyhegde6/actionCamMcp.wiki` as a normal REST repository or create a Git blob there. The connector can access the source repository but its repository-scoped Git Data API does not expose the Wiki Git remote. This is a connector/API boundary, not evidence that the Wiki needs initialization.

Use an actual Codex Local or Cloud shell with Git, network access and authorized credentials to run `git clone https://github.com/luckyhegde6/actionCamMcp.wiki.git`, update the existing pages, commit and push. Do not retry the REST Git Data calls against the `.wiki` name after this 404 has been confirmed.

## Recommended publication flow

```text
Normal repository docs + assets
          |
          v
Review and commit through Codex
          |
          v
Create/refresh Wiki working copy
          |
          v
Update existing Wiki pages + images
          |
          v
Commit and push Wiki default branch
          |
          v
Fetch live pages and verify links/images
```

Do not assume a commit in the normal repository automatically updates the Wiki. They have independent histories.

## Codex connector versus Codex

The GitHub app in ChatGPT is useful for repository search and read-only analysis. Use Codex when changes must be made, tested, committed, pushed or proposed as a pull request. Depending on the ChatGPT client, Codex can run in Cloud, Local or Worktree mode. The chosen account must have access to the repository; the environment must also have the required tools, network access and credentials.

See:
- [ChatGPT Codex + GitHub skill](../skills/chatgpt-codex-github-workflow/SKILL.md)
- [GitHub Wiki Git Publishing skill](../skills/github-wiki-git-publishing/SKILL.md)

## Local Wiki publisher script

The repository includes `scripts/publish_wiki.py` to repair stale image references and publish the Wiki from a local checkout. Run it from the source repository root after pulling the latest `main` branch.

```powershell
# 1. Preview the changes (clones/refreshes the Wiki in your OS temp directory)
python scripts/publish_wiki.py

# 2. Apply locally and validate every Markdown image target
python scripts/publish_wiki.py --apply

# 3. Commit and publish to the Wiki default branch
python scripts/publish_wiki.py --apply --push
```

The script uses your normal Git credential manager session; it never asks for a token in command-line arguments. It copies only raster assets from `docs/assets/` into the Wiki's `images/` folder, replaces the deleted-branch raw URLs, replaces the missing storyboard SVG with the six existing JPEG shots, validates local image targets, and refuses to force-push. The Wiki checkout is retained under the operating system temporary directory at `actioncam-mcp-wiki`; use `--wiki-dir` to choose another location.

Use `--apply` to edit and stage the Wiki working copy without publishing. Only add `--push` when the preview is correct and you intend to publish immediately. The script requires Git, network access to github.com, and Wiki write permission.


## Safe publishing checklist

- Inspect the current repository and Wiki before editing.
- Preserve existing pages, sidebar and footer.
- Use PNG/JPEG/GIF raster illustrations; this project does not use SVG.
- Use relative image references for assets committed in the Wiki repository.
- Push only to the Wiki default branch to publish.
- Verify the live page and every image after pushing.
- Report commit SHA, URLs and any permission or initialization blockers.

## Official references

- [GitHub: Adding or editing Wiki pages](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages)
- [GitHub: Editing Wiki content and adding images](https://docs.github.com/en/communities/documenting-your-project-with-wikis/editing-wiki-content)
- [OpenAI: Connecting GitHub to ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt)
- [OpenAI: Codex Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
