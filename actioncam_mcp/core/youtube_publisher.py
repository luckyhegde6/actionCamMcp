"""
YouTube Export & Publish Helper for ActionCam MCP Studio.
Combines reference discovery / metadata extraction (inspired by ia-programming/youtube-mcp)
with YouTube Data API v3 resumable upload & SEO sidecar generation for exports/YouTube/.
"""

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


class YouTubePublisher:
    """Prepares YouTube SEO metadata sidecars, searches reference videos, and uploads via OAuth2."""

    def __init__(self, oauth_token: Optional[str] = None):
        self.oauth_token = oauth_token or os.getenv("YOUTUBE_OAUTH_TOKEN")

    @staticmethod
    def generate_youtube_metadata(
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        category_id: str = "22",
        privacy_status: str = "private",
        chapters: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Builds a YouTube Data API v3 snippet + status payload."""
        desc_lines = [description.strip()] if description else []
        if chapters:
            desc_lines.append("\nChapters:")
            for ch in chapters:
                desc_lines.append(f"{ch.get('time', '00:00')} {ch.get('title', 'Section')}")
        return {
            "snippet": {
                "title": title[:100],
                "description": "\n".join(desc_lines).strip(),
                "tags": tags or ["DJI Action 4", "DaVinci Resolve", "Travel"],
                "categoryId": str(category_id),
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

    @classmethod
    def write_metadata_sidecar(cls, video_path: str, metadata: Dict[str, Any]) -> Path:
        """Writes `<video>.youtube.json` next to the exported YouTube MP4."""
        vpath = Path(video_path)
        sidecar = vpath.with_suffix(".youtube.json")
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return sidecar

    def upload_video_resumable(
        self,
        video_path: str,
        metadata: Dict[str, Any],
        execute_upload: bool = False,
    ) -> Dict[str, Any]:
        """
        Writes the `.youtube.json` metadata sidecar and, when `execute_upload=True`
        with `YOUTUBE_OAUTH_TOKEN` set, performs a YouTube Data API v3 resumable upload.
        """
        vpath = Path(video_path)
        sidecar = self.write_metadata_sidecar(str(vpath), metadata)
        result: Dict[str, Any] = {
            "video_path": str(vpath),
            "metadata_sidecar": str(sidecar),
            "title": metadata["snippet"]["title"],
            "privacy_status": metadata["status"]["privacyStatus"],
        }

        if not execute_upload or not self.oauth_token:
            result["status"] = "Prepared (set YOUTUBE_OAUTH_TOKEN and execute_upload=True to publish)"
            return result

        if not vpath.exists():
            result["status"] = "Error: video file not found"
            return result

        init_req = urllib.request.Request(
            YOUTUBE_UPLOAD_URL,
            data=json.dumps(metadata).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.oauth_token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Length": str(vpath.stat().st_size),
                "X-Upload-Content-Type": "video/mp4",
            },
            method="POST",
        )
        with urllib.request.urlopen(init_req, timeout=30) as resp:
            upload_session_url = resp.headers.get("Location")

        if not upload_session_url:
            result["status"] = "Error: missing resumable upload Location header"
            return result

        video_bytes = vpath.read_bytes()
        put_req = urllib.request.Request(
            upload_session_url,
            data=video_bytes,
            headers={"Content-Type": "video/mp4"},
            method="PUT",
        )
        with urllib.request.urlopen(put_req, timeout=300) as resp:
            uploaded = json.loads(resp.read().decode("utf-8"))

        result["status"] = "Uploaded"
        result["video_id"] = uploaded.get("id")
        result["url"] = f"https://www.youtube.com/watch?v={uploaded.get('id')}" if uploaded.get("id") else None
        return result

    @staticmethod
    def search_reference_videos(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Lightweight YouTube reference search without API key (inspired by ia-programming/youtube-mcp).
        Returns video IDs, titles, and watch URLs for edit inspiration.
        """
        q = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={q}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"([^"]+)"\}', html)
        seen = set()
        results: List[Dict[str, str]] = []
        for vid, title in matches:
            if vid in seen:
                continue
            seen.add(vid)
            results.append({
                "video_id": vid,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={vid}",
            })
            if len(results) >= max_results:
                break
        return results
