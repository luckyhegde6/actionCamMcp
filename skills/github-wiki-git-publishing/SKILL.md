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

GitHub Wiki pages can be publicly visible in the web UI while the Wiki Git remote remains unavailable through the standard GitHub REST repository endpoints. Do not infer that a published Wiki is uninitialized just because `GET /repos/OWNER/REPO.wiki` returns 404. Confirm the public Wiki page separately, then test the Git remote with `git ls-remote https://github.com/OWNER/REPO.wiki.git` or `git clone`. A successful public page fetch proves publication, not Git transport or connector write access.

## Preferred workflow: use the repository publisher script

From the local source-repository root, first pull the latest `main`, then use the maintained publisher:

```powershell
python scripts/publish_wiki.py
python scripts/publish_wiki.py --apply
python scripts/publish_wiki.py --apply --push
```

The first command is report-only. The second applies and validates the repair in the local Wiki checkout. The third commits and pushes to the Wiki default branch. The script clones or fast-forwards `https://github.com/luckyhegde6/actionCamMcp.wiki.git`, copies required raster files from `docs/assets/` into the Wiki `images/` folder, replaces stale deleted-branch image URLs, replaces the missing storyboard SVG with the six-shot JPEG gallery, validates image targets, and never force-pushes. It uses the user's existing Git credential manager session.

Use `--wiki-dir PATH` to select a persistent checkout location. The default is the OS temporary directory's `actioncam-mcp-wiki` folder.

If the script reports Git transport, authentication, or permission errors, stop and resolve those locally. Do not fall back to GitHub Contents API calls against the `.wiki` repository; the standard connector does not expose that Git remote.

## Manual workflow details

Run this in a local Codex workspace or a Codex Cloud environment that has Git, network access to github.com, and credentials with Wiki write permission.

```bash
git clone https://github.com/OWNER/REPO.wiki.git
cd REPO.wiki
git remote -v
git branch --show-current
git pull --ff-only
```

If `git ls-remote` or `git clone` fails, capture the exact Git transport error. If the Wiki page is already visible, do not ask the owner to initialize it again; check authentication, network access, repository policy and whether the environment supports Git over HTTPS. Do not fabricate a Wiki repository or replace the source repository.

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

## GitHub connector/API limitation

The ChatGPT GitHub connector exposes repository-scoped REST actions such as Contents and Git Data operations. In this workflow, the connector successfully resolves `luckyhegde6/actionCamMcp` but returns `404 Not Found` for `luckyhegde6/actionCamMcp.wiki` when calling `get_repo` and `create_blob`. This can happen even while the public Wiki pages are already published and visible in the browser: the Wiki Git remote is not exposed as a normal repository resource through these connector actions.

Do not retry `create_blob`, `create_tree`, `create_commit` or `update_ref` against `OWNER/REPO.wiki` after the connector has established this 404 boundary. Those actions cannot publish Wiki pages through this connector. Use an actual Codex Local or Cloud shell with Git transport and authorized credentials to clone, commit and push `https://github.com/OWNER/REPO.wiki.git`. The connector can still update the normal source repository; it cannot substitute for Git push to the Wiki remote. Always verify the live Wiki after a push.

## Troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| Public Wiki page works but GitHub REST connector returns 404 for `OWNER/REPO.wiki` | Wiki Git remote is not exposed as a normal REST repository to that connector | Do not reinitialize the Wiki; use Codex Local/Cloud Git transport with authorized credentials |
| Clone prompts for credentials | Private Wiki or missing credentials | Use the signed-in Git credential flow; never request a password in chat |
| Push rejected | Remote changed or caller lacks Wiki write access | Fetch/pull and reconcile; do not force-push |
| Page exists but image is broken | Wrong relative path/case or uncommitted image | Verify file path and commit image |
| Markdown page not visible | Change pushed to non-default branch | Merge/push to Wiki default branch |
| Main repo API works but Wiki Git Data actions return 404 | Connector's repository-scoped API does not expose the Wiki Git remote | Switch to an actual Git clone/push environment; keep normal-repo and Wiki commits separate |

## Official references

- GitHub Docs — [Adding or editing Wiki pages](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages)
- GitHub Docs — [Editing Wiki content and adding images](https://docs.github.com/en/communities/documenting-your-project-with-wikis/editing-wiki-content)
- GitHub Docs — [Documenting your project with Wikis](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
