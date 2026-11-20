# GitHub Wiki and ChatGPT Codex Publishing Workflow

This project uses two separate Git destinations:

1. **Normal repository** (`luckyhegde6/actionCamMcp`): canonical source for camera lessons, diagrams, project documentation and reusable agent guidance.
2. **GitHub Wiki** (`luckyhegde6/actionCamMcp.wiki.git`): reader-facing long-form Wiki pages and their image assets.

## Why the Wiki API returned 404

GitHub's documentation says the Wiki can be cloned after an initial Wiki page has been created. A repository with Wikis enabled can therefore still return 404 for the `.wiki.git` repository until the first page exists. The first page can be initialized through the repository's Wiki UI; after that, use normal Git clone/commit/push.

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
