#!/usr/bin/env python3
"""Repair and publish the ActionCam GitHub Wiki from the local source assets.

The source repository and its Wiki are separate Git repositories. This script
clones/fast-forwards the Wiki, copies referenced raster assets from docs/assets,
repairs stale image URLs, validates Markdown image targets, and optionally
commits/pushes to the Wiki default branch.

Safe by default: without --apply it only reports the proposed changes.
Publishing requires both --apply and --push.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote


OWNER = "luckyhegde6"
REPO = "actionCamMcp"
WIKI_URL = f"https://github.com/{OWNER}/{REPO}.wiki.git"
OLD_ASSET_PREFIX = (
    f"https://raw.githubusercontent.com/{OWNER}/{REPO}/"
    "docs/phase-1-visual-learning-wiki/docs/assets/"
)
CURRENT_ASSET_PREFIX = (
    f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/docs/assets/"
)
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}

SHOT_SEQUENCE = [
    ("shot-01-establishing.jpg", "Establishing shot"),
    ("shot-02-detail.jpg", "Detail shot"),
    ("shot-03-walking-movement.jpg", "Walking movement"),
    ("shot-04-electronics-activity.jpg", "Activity / action"),
    ("shot-05-pov-trail.jpg", "Point of view"),
    ("shot-06-closing-sunset.jpg", "Closing shot"),
]


def run_git(args: list[str], cwd: Path | None = None, *, capture: bool = True) -> str:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )
    if result.returncode:
        details = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n{details}")
    return (result.stdout or "").strip()


def find_repo_root(start: Path) -> Path:
    output = run_git(["rev-parse", "--show-toplevel"], start)
    return Path(output).resolve()


def ensure_wiki_checkout(wiki_dir: Path) -> str:
    if (wiki_dir / ".git").exists():
        remote = run_git(["remote", "get-url", "origin"], wiki_dir)
        if remote.rstrip("/").lower() != WIKI_URL.rstrip("/").lower():
            raise RuntimeError(
                f"{wiki_dir} is already a Git repository with unexpected origin: {remote}"
            )
        run_git(["fetch", "origin", "--prune"], wiki_dir)
        head = run_git(
            ["symbolic-ref", "refs/remotes/origin/HEAD"], wiki_dir
        ) if has_remote_head(wiki_dir) else ""
        branch = head.rsplit("/", 1)[-1] if head else run_git(
            ["branch", "--show-current"], wiki_dir
        )
        if not branch:
            raise RuntimeError("Could not determine the Wiki default branch.")
        run_git(["checkout", branch], wiki_dir)
        run_git(["pull", "--ff-only", "origin", branch], wiki_dir)
        return branch

    if wiki_dir.exists() and any(wiki_dir.iterdir()):
        raise RuntimeError(
            f"Wiki working directory is not empty and is not a Git checkout: {wiki_dir}"
        )
    wiki_dir.parent.mkdir(parents=True, exist_ok=True)
    run_git(["clone", WIKI_URL, str(wiki_dir)], capture=True)
    branch = run_git(["branch", "--show-current"], wiki_dir)
    if not branch:
        raise RuntimeError("Wiki clone has no checked-out default branch.")
    return branch


def has_remote_head(wiki_dir: Path) -> bool:
    result = subprocess.run(
        ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd=wiki_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def image_gallery(asset_dir: Path) -> str:
    missing = [filename for filename, _ in SHOT_SEQUENCE if not (asset_dir / filename).is_file()]
    if missing:
        raise RuntimeError(
            "Cannot replace the missing SVG storyboard; source assets are missing: "
            + ", ".join(missing)
        )

    rows = ["| | |", "|---|---|"]
    for index in range(0, len(SHOT_SEQUENCE), 2):
        cells = []
        for filename, caption in SHOT_SEQUENCE[index:index + 2]:
            cells.append(
                f"![{caption}](images/{filename})\\n\\n*{caption}*"
            )
        rows.append("| " + " | ".join(cells) + " |")
    return "\\n".join(rows)


def repair_page(text: str, asset_dir: Path) -> tuple[str, set[str], int]:
    copied_assets: set[str] = set()
    replacements = 0

    def replace_missing_storyboard(match: re.Match[str]) -> str:
        nonlocal replacements
        replacements += 1
        return image_gallery(asset_dir)

    storyboard_pattern = re.compile(
        r"!\\[[^\\]]*\\]\\([^)]*first-video-shot-sequence\\.svg(?:\\s+[^)]*)?\\)",
        re.IGNORECASE,
    )
    text = storyboard_pattern.sub(replace_missing_storyboard, text)

    # Replace old branch URLs and already-updated main raw URLs with portable
    # Wiki-relative image paths, copying only assets that exist in docs/assets.
    url_pattern = re.compile(
        re.escape(OLD_ASSET_PREFIX) + r"([^\\s)\\\"'>]+)"
        + "|" + re.escape(CURRENT_ASSET_PREFIX) + r"([^\\s)\\\"'>]+)"
    )

    def replace_asset_url(match: re.Match[str]) -> str:
        nonlocal replacements
        filename = unquote(match.group(1) or match.group(2)).split("?")[0]
        source = asset_dir / Path(filename).name
        if source.suffix.lower() not in RASTER_EXTENSIONS or not source.is_file():
            return match.group(0)
        copied_assets.add(source.name)
        replacements += 1
        return f"images/{source.name}"

    text = url_pattern.sub(replace_asset_url, text)

    # Remove stale placeholder wording after the storyboard has been inserted.
    if "first-video-shot-sequence.svg" not in text:
        text = re.sub(
            r"(?im)^.*(?:six-shot|shot-sequence|storyboard).*(?:pending upload|not yet uploaded|will be added later).*(?:\\n|$)",
            "",
            text,
        )
    return text, copied_assets, replacements


def validate_wiki(wiki_dir: Path) -> list[str]:
    errors: list[str] = []
    for page in sorted(wiki_dir.glob("*.md")):
        content = page.read_text(encoding="utf-8")
        for match in re.finditer(r"!\\[[^\\]]*\\]\\(([^)]+)\\)", content):
            target = match.group(1).strip().split()[0].strip("<>")
            if re.match(r"^(?:https?:|data:)", target, re.IGNORECASE):
                if target.lower().endswith(".svg"):
                    errors.append(f"{page.name}: SVG image reference is not allowed: {target}")
                continue
            if target.startswith("#"):
                continue
            local_target = unquote(target.split("#", 1)[0])
            if not local_target:
                continue
            if not (page.parent / local_target).is_file():
                errors.append(f"{page.name}: missing image target: {target}")
            elif Path(local_target).suffix.lower() not in RASTER_EXTENSIONS:
                errors.append(f"{page.name}: unsupported image format: {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair broken ActionCam Wiki image references and publish the Wiki."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="write repairs to the Wiki checkout (default is report-only)",
    )
    parser.add_argument(
        "--push", action="store_true",
        help="commit and push repairs to the Wiki default branch (requires --apply)",
    )
    parser.add_argument(
        "--wiki-dir", type=Path,
        help="persistent Wiki clone directory (default: system temp/actioncam-mcp-wiki)",
    )
    parser.add_argument(
        "--message", default="docs(wiki): repair image links and publish raster storyboard",
        help="Wiki commit message",
    )
    args = parser.parse_args()

    if args.push and not args.apply:
        parser.error("--push requires --apply")

    try:
        root = find_repo_root(Path.cwd())
        asset_dir = root / "docs" / "assets"
        if not asset_dir.is_dir():
            raise RuntimeError(f"Source asset directory not found: {asset_dir}")

        wiki_dir = (
            args.wiki_dir.expanduser().resolve()
            if args.wiki_dir
            else Path(tempfile.gettempdir()) / "actioncam-mcp-wiki"
        )
        branch = ensure_wiki_checkout(wiki_dir)
        print(f"Wiki checkout: {wiki_dir}")
        print(f"Wiki branch:   {branch}")

        changed_pages: list[str] = []
        all_assets: set[str] = set()
        total_replacements = 0

        for page in sorted(wiki_dir.glob("*.md")):
            original = page.read_text(encoding="utf-8")
            updated, assets, count = repair_page(original, asset_dir)
            if updated != original:
                changed_pages.append(page.name)
                total_replacements += count
                all_assets.update(assets)
                if args.apply:
                    page.write_text(updated, encoding="utf-8", newline="\\n")

        if args.apply:
            image_dir = wiki_dir / "images"
            image_dir.mkdir(exist_ok=True)
            for filename in sorted(all_assets):
                shutil.copy2(asset_dir / filename, image_dir / filename)
            # Storyboard files are required only if the missing SVG was present.
            has_storyboard = any(
                "shot-01-establishing.jpg" in page.read_text(encoding="utf-8")
                for page in wiki_dir.glob("*.md")
            )
            if has_storyboard:
                for filename, _ in SHOT_SEQUENCE:
                    shutil.copy2(asset_dir / filename, image_dir / filename)

        print(f"Pages requiring changes: {len(changed_pages)}")
        for name in changed_pages:
            print(f"  - {name}")
        print(f"Image URL / storyboard replacements: {total_replacements}")
        print(f"Raster assets to copy: {len(all_assets)}")

        if not args.apply:
            print("\\nDry run only. Re-run with --apply to modify the Wiki checkout.")
            return 0

        errors = validate_wiki(wiki_dir)
        if errors:
            print("\\nWiki image validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 2

        status = run_git(["status", "--short"], wiki_dir)
        if not status:
            print("Wiki is already up to date; no commit needed.")
            return 0

        print("\\nChanged files:")
        print(status)
        run_git(["add", "-A"], wiki_dir)
        run_git(["diff", "--cached", "--check"], wiki_dir)

        if args.push:
            run_git(["commit", "-m", args.message], wiki_dir)
            run_git(["push", "origin", branch], wiki_dir, capture=False)
            commit = run_git(["rev-parse", "HEAD"], wiki_dir)
            print(f"\\nPublished Wiki commit: {commit}")
            print(f"Live Wiki: https://github.com/{OWNER}/{REPO}/wiki")
        else:
            print(
                "\\nRepairs are staged locally but not committed or published. "
                "Re-run with --apply --push to publish."
            )
        return 0

    except (RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "\\nCheck Git installation, network access, Git Credential Manager "
            "sign-in, and Wiki write permission.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
