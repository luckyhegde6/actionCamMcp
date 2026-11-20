---
name: github-wiki-git-publishing
description: Publish and maintain GitHub Wiki pages using the Wiki Git repository, including raster images, Markdown pages, safe initialization, verification, and troubleshooting.
---

# GitHub Wiki Git Publishing

Use this skill when a task must publish or update pages in a repository's GitHub Wiki. The normal source repository and its Wiki are separate Git repositories with separate histories and permissions.

## Important repository distinction

For a source repository `OWNER/REPO`, the Wiki Git remote is:

```text
https://github.com/OWNER/REPO.wiki.git
```

The Wiki repository is not a normal subdirectory of the source repository. Do not assume the source repository's GitHub Contents API can read or write Wiki pages.

GitHub documents that the Wiki Git repository becomes clonable after an initial Wiki page has been created. A 404 for `OWNER/REPO.wiki` before that initialization is not proof that the source repository is missing or that Wiki is disabled. First check that the repository has `has_wiki=true` and whether the Wiki has an initial page.

## Preferred workflow: clone, edit, commit, push

Run this in a local Codex workspace or a Codex Cloud environment that has Git, network access to github.com, and credentials with Wiki write permission.

```bash
git clone https://github.com/OWNER/REPO.wiki.git
cd REPO.wiki
git remote -v
git branch --show-current
git pull --ff-only
```

If the Wiki is not initialized, stop and ask the repository owner to create its first page through GitHub's Wiki UI. Then retry the clone. Do not fabricate a Wiki repository or replace the source repository.

Create or update page files in Markdown. The filename becomes the page title; use hyphens for spaces, avoid reserved filename characters, and preserve existing pages.

Example:
```text
Getting-Started.md
Phase-1.2-Exposure.md
Phase-1.3-Frame-Rates-and-Slow-Motion.md
Phase-1.4-Colour-Profiles-CST-and-Rec.709.md
Phase-1.5-Media-Workflow-and-Resolve-Performance.md
_Discussion.md
_Sidebar.md
_Footer.md
```

Before changing pages:
1. Pull the latest default branch.
2. List all existing files and inspect the relevant pages and sidebar.
3. Identify the current page naming conventions and inbound links.
4. Make the smallest change; do not replace unrelated Wiki content.
5. Preserve custom sidebar/footer files if present.

## Raster image publishing

GitHub Wiki supports PNG, JPEG and GIF images. Do not use SVG for this workflow.

Recommended layout:
```text
REPO.wiki/
├── Getting-Started.md
├── Phase-1.2-Exposure.md
├── Phase-1.3-Frame-Rates-and-Slow-Motion.md
├── Phase-1.4-Colour-Profiles-CST-and-Rec.709.md
├── Phase-1.5-Media-Workflow-and-Resolve-Performance.md
└── images/
    ├── six-shot-mini-story.png
    ├── exposure-controls-review.png
    ├── frame-rates-slow-motion.png
    ├── colour-profile-rec709-pipeline.png
    └── media-ingest-proxy-workflow.png
```

Embed with Markdown relative paths:
```markdown
![Six-shot mini-story storyboard](images/six-shot-mini-story.png)
```

Keep image filenames stable, descriptive and lowercase. Use alt text that explains the image's purpose. Optimize large images without making labels unreadable. Do not embed screenshots that are not actual product UI as if they were camera screenshots; label illustrations as diagrams.

If images live in the normal source repository rather than the Wiki repository, GitHub documents that they can be linked by their repository URL. For portable Wiki maintenance, prefer committing the image files to the Wiki Git repository's `images/` folder.

## Commit and publish

Wiki pages are live only after their commits reach the Wiki's default branch.

```bash
git status --short
git add Getting-Started.md Phase-1.2-Exposure.md images/
git diff --cached --check
git diff --cached --stat
git commit -m "docs: update ActionCam learning wiki"
git push origin HEAD
```

Do not force-push. If a branch is used for collaboration, merge or fast-forward it into the Wiki default branch; pushing a non-default branch alone does not publish the page.

## Verification checklist

After pushing:
- Fetch the Wiki default branch again.
- Confirm the expected page files exist.
- Confirm every Markdown image target exists and is a PNG/JPEG/GIF.
- Open the live Wiki pages in a browser and verify rendering.
- Check all internal links, including page names with spaces encoded by GitHub.
- Verify the Getting Started page links to all phase pages.
- Confirm the old illustration is replaced, not duplicated.
- Report exact live URLs and commit SHA.

## GitHub API alternative

The GitHub REST Contents and Git Data APIs operate on a repository. The Wiki has its own Git remote and Git history; it is not a special `/wiki` path in the normal source repository API.

If a GitHub App/connector can access the Wiki repository as a repository, it may be possible to use Git Data API operations (create blobs, trees, commits, update the default branch ref). This is conditional on the Wiki repository being initialized and the connector granting write access to it. The Contents API may return 404 for the Wiki repository before its first page exists. Never claim a Wiki API write succeeded without fetching the live Wiki result.

## Troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| `OWNER/REPO.wiki` returns 404 | Wiki has not been initialized, or caller lacks access | Check `has_wiki`; create the initial page in the Wiki UI; retry |
| Clone prompts for credentials | Private Wiki or missing credentials | Use the signed-in Git credential flow; never request a password in chat |
| Push rejected | Remote changed or caller lacks Wiki write access | Fetch/pull and reconcile; do not force-push |
| Page exists but image is broken | Wrong relative path/case or uncommitted image | Verify file path and commit image |
| Markdown page not visible | Change pushed to non-default branch | Merge/push to Wiki default branch |
| Main repo API works but Wiki API returns 404 | Separate repository and permission boundary | Do not infer Wiki write permission from source-repo access |

## Official references

- GitHub Docs — [Adding or editing Wiki pages](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages)
- GitHub Docs — [Editing Wiki content and adding images](https://docs.github.com/en/communities/documenting-your-project-with-wikis/editing-wiki-content)
- GitHub Docs — [Documenting your project with Wikis](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
