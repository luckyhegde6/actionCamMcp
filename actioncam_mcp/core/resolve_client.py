"""
DaVinci Resolve Studio Automation Client.
Provides a high-level Python API over Blackmagic Design's DaVinciResolveScript.
"""

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from ..config import (
    RESOLVE_SCRIPT_API_DEFAULT,
    RESOLVE_SCRIPT_LIB_DEFAULT,
    RESOLVE_MODULES_PATH_DEFAULT,
    MEDIA_POOL_BINS,
    EXPORT_PROFILES,
)

logger = logging.getLogger("actioncam_mcp.resolve")

class ResolveClient:
    """Wrapper around DaVinci Resolve Scripting API."""

    def __init__(self, api_path: Optional[str] = None, lib_path: Optional[str] = None):
        self.api_path = api_path or os.getenv("RESOLVE_SCRIPT_API", RESOLVE_SCRIPT_API_DEFAULT)
        self.lib_path = lib_path or os.getenv("RESOLVE_SCRIPT_LIB", RESOLVE_SCRIPT_LIB_DEFAULT)
        self.modules_path = RESOLVE_MODULES_PATH_DEFAULT
        
        self._dvr = None
        self._resolve = None
        self._fusion = None
        self._project_manager = None
        self._current_project = None
        self._media_pool = None
        
        self._init_environment()

    def _init_environment(self):
        """Sets required environment variables and sys.path for DaVinciResolveScript."""
        if self.api_path and os.path.exists(self.api_path):
            os.environ["RESOLVE_SCRIPT_API"] = self.api_path
        if self.lib_path and os.path.exists(self.lib_path):
            os.environ["RESOLVE_SCRIPT_LIB"] = self.lib_path
        if self.modules_path and os.path.exists(self.modules_path):
            if self.modules_path not in sys.path:
                sys.path.insert(0, self.modules_path)

    def connect(self) -> bool:
        """Attempts to connect to a running DaVinci Resolve Studio instance."""
        try:
            self._init_environment()
            import DaVinciResolveScript as dvr
            self._dvr = dvr
            self._resolve = dvr.scriptapp("Resolve")
            
            if self._resolve:
                self._fusion = self._resolve.Fusion()
                self._project_manager = self._resolve.GetProjectManager()
                self._current_project = self._project_manager.GetCurrentProject() if self._project_manager else None
                if self._current_project:
                    self._media_pool = self._current_project.GetMediaPool()
                logger.info(f"Connected to DaVinci Resolve {self.get_version()}")
                return True
            else:
                logger.warning("DaVinci Resolve is not running or external scripting is disabled.")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to DaVinci Resolve: {e}")
            return False

    def is_connected(self) -> bool:
        """Checks if connection to Resolve is alive."""
        if not self._resolve:
            return self.connect()
        try:
            # Ping resolve by calling GetVersion
            _ = self._resolve.GetVersion()
            return True
        except Exception:
            self._resolve = None
            return False

    def get_version(self) -> str:
        """Returns DaVinci Resolve version string."""
        if self.is_connected():
            return ".".join(str(x) for x in self._resolve.GetVersion())
        return "Not Connected"

    def get_project_manager(self):
        """Returns the ProjectManager instance."""
        if self.is_connected():
            self._project_manager = self._resolve.GetProjectManager()
            return self._project_manager
        return None

    def get_current_project(self):
        """Returns the active Project instance."""
        pm = self.get_project_manager()
        if pm:
            self._current_project = pm.GetCurrentProject()
            return self._current_project
        return None

    def create_project(self, project_name: str, resolution: Tuple[int, int] = (1920, 1080), fps: float = 25.0) -> Optional[Any]:
        """Creates a new project or loads it if it already exists."""
        pm = self.get_project_manager()
        if not pm:
            raise RuntimeError("Cannot access ProjectManager - DaVinci Resolve is not connected.")

        # Try to load existing first
        proj = pm.LoadProject(project_name)
        if not proj:
            proj = pm.CreateProject(project_name)
            logger.info(f"Created new project: {project_name}")
        else:
            logger.info(f"Loaded existing project: {project_name}")

        self._current_project = proj
        if proj:
            self._media_pool = proj.GetMediaPool()
            # Set project settings
            self.set_project_settings(resolution, fps)
        return proj

    def set_project_settings(self, resolution: Tuple[int, int] = (1920, 1080), fps: float = 25.0) -> bool:
        """Sets project timeline resolution and frame rate."""
        proj = self.get_current_project()
        if not proj:
            return False

        width, height = resolution
        settings = {
            "timelineResolutionWidth": str(width),
            "timelineResolutionHeight": str(height),
            "timelineFrameRate": str(fps),
            "timelinePlaybackFrameRate": str(fps),
        }
        for k, v in settings.items():
            proj.SetSetting(k, v)
        logger.info(f"Applied project settings: {width}x{height} @ {fps}fps")
        return True

    def get_media_pool(self):
        """Returns current MediaPool."""
        proj = self.get_current_project()
        if proj:
            self._media_pool = proj.GetMediaPool()
            return self._media_pool
        return None

    def create_bin_structure(self, bin_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Creates a structured hierarchy of bins in the Media Pool.
        Supports nested paths like '01 Raw Footage/Slow Motion'.
        """
        mp = self.get_media_pool()
        if not mp:
            raise RuntimeError("MediaPool not available.")

        bin_paths = bin_paths or MEDIA_POOL_BINS
        root_folder = mp.GetRootFolder()
        created_folders = {"": root_folder}

        for path in bin_paths:
            parts = path.replace("\\", "/").strip("/").split("/")
            parent_key = ""
            current_folder = root_folder

            for part in parts:
                full_key = f"{parent_key}/{part}".strip("/") if parent_key else part
                if full_key in created_folders:
                    current_folder = created_folders[full_key]
                else:
                    # Check if already exists in parent's subfolders
                    existing = None
                    for sub in current_folder.GetSubFolderList():
                        if sub.GetName() == part:
                            existing = sub
                            break
                    if existing:
                        current_folder = existing
                    else:
                        new_folder = mp.AddSubFolder(current_folder, part)
                        current_folder = new_folder
                    created_folders[full_key] = current_folder
                parent_key = full_key

        logger.info(f"Created {len(created_folders)} bins in Media Pool")
        return created_folders

    def import_media(self, file_paths: List[str], target_folder_key: Optional[str] = None) -> List[Any]:
        """
        Imports files into the Media Pool, optionally into a specific bin folder.
        """
        mp = self.get_media_pool()
        if not mp:
            raise RuntimeError("MediaPool not available.")

        # Set target folder if specified
        if target_folder_key:
            folders = self.create_bin_structure()
            target_folder = folders.get(target_folder_key)
            if target_folder:
                mp.SetCurrentFolder(target_folder)

        # Import media
        normalized_paths = [os.path.normpath(p) for p in file_paths if os.path.exists(p)]
        if not normalized_paths:
            logger.warning("No valid files to import.")
            return []

        imported_items = mp.ImportMedia(normalized_paths)
        logger.info(f"Imported {len(imported_items)} items into Media Pool")
        return imported_items

    def find_media_item_by_name(self, name: str) -> Optional[Any]:
        """Recursively searches for a MediaPoolItem matching clip name."""
        mp = self.get_media_pool()
        if not mp:
            return None

        def search_folder(folder):
            for clip in folder.GetClipList():
                if clip.GetName() == name or clip.GetClipProperty("File Path") == name:
                    return clip
            for sub in folder.GetSubFolderList():
                res = search_folder(sub)
                if res:
                    return res
            return None

        return search_folder(mp.GetRootFolder())

    def get_all_media_items(self) -> List[Any]:
        """Recursively collects all MediaPoolItems from all bins."""
        mp = self.get_media_pool()
        if not mp:
            return []

        items = []
        def collect(folder):
            items.extend(folder.GetClipList())
            for sub in folder.GetSubFolderList():
                collect(sub)

        collect(mp.GetRootFolder())
        return items

    def detect_scene_cuts_on_reference(self, reference_path: str, timeline_name: str = "Ref_Decoded_Timeline") -> List[Dict[str, Any]]:
        """
        Imports a reference video, adds it to a dedicated timeline, triggers DaVinci Resolve's
        Neural Engine DetectSceneCuts(), and retrieves all cut segments.
        """
        mp = self.get_media_pool()
        proj = self.get_current_project()
        if not mp or not proj:
            raise RuntimeError("Resolve is not connected.")

        # Ensure bins exist
        folders = self.create_bin_structure()
        ref_folder = folders.get("02 Reference Edits", mp.GetRootFolder())
        mp.SetCurrentFolder(ref_folder)

        # Import reference clip
        imported = mp.ImportMedia([os.path.normpath(reference_path)])
        if not imported:
            raise RuntimeError(f"Could not import reference video: {reference_path}")
        ref_clip = imported[0]

        # Create timeline from reference clip
        timeline = mp.CreateTimelineFromClips(timeline_name, [ref_clip])
        if not timeline:
            raise RuntimeError(f"Could not create timeline '{timeline_name}' from reference video")

        proj.SetCurrentTimeline(timeline)
        logger.info(f"Running DetectSceneCuts() on timeline '{timeline_name}'...")

        # Run scene cut detection
        success = timeline.DetectSceneCuts()
        if not success:
            logger.warning("DetectSceneCuts call returned False or not supported in this context.")

        # Poll status
        max_wait_seconds = 60
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            status_info = proj.GetDetectSceneCutsStatus()
            status = status_info.get("JobStatus", "Complete") if status_info else "Complete"
            percent = status_info.get("CompletionPercentage", 100) if status_info else 100
            logger.debug(f"Scene detection: {status} ({percent}%)")
            
            if status in ("Complete", "Inactive"):
                break
            time.sleep(0.5)

        # Retrieve all sliced timeline items from video track 1
        items = timeline.GetItemListInTrack("video", 1) or []
        cuts_data = []

        fps = float(proj.GetSetting("timelineFrameRate") or 25.0)
        
        for idx, item in enumerate(items):
            start = item.GetStart()
            end = item.GetEnd()
            duration = item.GetDuration()
            
            cuts_data.append({
                "shot_index": idx + 1,
                "start_frame": start,
                "end_frame": end,
                "duration_frames": duration,
                "duration_seconds": round(duration / fps, 3),
                "start_timecode": round(start / fps, 3),
            })

        logger.info(f"Decoded {len(cuts_data)} shots from reference video")
        return cuts_data

    def assemble_matched_timeline(
        self,
        timeline_name: str,
        shot_mappings: List[Dict[str, Any]],
        bgm_path: Optional[str] = None,
        sfx_entries: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        """
        Assembles a brand-new timeline using matched source clips based on reference cut timings.
        shot_mappings is a list of:
        {
            "media_pool_item": MediaPoolItem or clip_path,
            "start_frame": float,
            "end_frame": float,
            "record_frame": float,
            "lut_path": Optional[str],
            "speed": Optional[float]
        }
        """
        mp = self.get_media_pool()
        proj = self.get_current_project()
        if not mp or not proj:
            raise RuntimeError("Resolve is not connected.")

        timeline = mp.CreateEmptyTimeline(timeline_name)
        if not timeline:
            raise RuntimeError(f"Could not create timeline '{timeline_name}'")

        proj.SetCurrentTimeline(timeline)

        # Append video clips
        clip_append_list = []
        for mapping in shot_mappings:
            item = mapping.get("media_pool_item")
            if isinstance(item, str):
                item = self.find_media_item_by_name(item)
            if not item:
                continue

            clip_info = {
                "mediaPoolItem": item,
                "startFrame": float(mapping.get("start_frame", 0)),
                "endFrame": float(mapping.get("end_frame", mapping.get("duration", 50))),
                "recordFrame": float(mapping.get("record_frame", 0)),
                "mediaType": 1,  # Video only
                "trackIndex": 1,
            }
            clip_append_list.append(clip_info)

        if clip_append_list:
            appended_items = mp.AppendToTimeline(clip_append_list)
            logger.info(f"Appended {len(appended_items)} video items to timeline")

            # Apply LUTs if specified in mappings
            for idx, mapping in enumerate(shot_mappings):
                lut = mapping.get("lut_path")
                if lut and idx < len(appended_items):
                    try:
                        appended_items[idx].SetLUT(1, self.normalize_lut_path(lut))
                    except Exception as e:
                        logger.warning(f"Failed to apply LUT on item {idx}: {e}")

        # Add Audio BGM if provided
        if bgm_path and os.path.exists(bgm_path):
            bgm_imported = mp.ImportMedia([os.path.normpath(bgm_path)])
            if bgm_imported:
                bgm_item = bgm_imported[0]
                mp.AppendToTimeline([{
                    "mediaPoolItem": bgm_item,
                    "startFrame": 0,
                    "recordFrame": 0,
                    "mediaType": 2,  # Audio only
                    "trackIndex": 1,
                }])
                logger.info(f"Appended BGM to Audio Track 1: {bgm_path}")

        # Add SFX if provided
        if sfx_entries:
            for sfx in sfx_entries:
                sfx_path = sfx.get("path")
                record_frame = sfx.get("record_frame", 0)
                track_idx = sfx.get("track_index", 2)
                if sfx_path and os.path.exists(sfx_path):
                    sfx_imported = mp.ImportMedia([os.path.normpath(sfx_path)])
                    if sfx_imported:
                        mp.AppendToTimeline([{
                            "mediaPoolItem": sfx_imported[0],
                            "startFrame": 0,
                            "recordFrame": record_frame,
                            "mediaType": 2,  # Audio only
                            "trackIndex": track_idx,
                        }])

        return timeline

    def setup_render_job(
        self,
        target_dir: str,
        custom_name: str,
        profile_key: str = "youtube_4k",
        custom_settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Configures the Deliver page with specified render profile and adds to Render Queue.
        """
        proj = self.get_current_project()
        if not proj:
            raise RuntimeError("Resolve is not connected.")

        os.makedirs(target_dir, exist_ok=True)
        profile = EXPORT_PROFILES.get(profile_key, EXPORT_PROFILES["youtube_4k"])

        render_settings = {
            "SelectAllFrames": True,
            "TargetDir": os.path.normpath(target_dir),
            "CustomName": custom_name,
        }

        # Apply custom overrides
        if custom_settings:
            render_settings.update(custom_settings)

        proj.SetRenderSettings(render_settings)
        job_id = proj.AddRenderJob()
        logger.info(f"Created Render Job ID: {job_id} for profile {profile['name']}")
        return job_id

    def start_rendering(self, job_ids: Optional[List[str]] = None) -> bool:
        """Starts rendering queued jobs."""
        proj = self.get_current_project()
        if not proj:
            return False
        if job_ids:
            return proj.StartRendering(job_ids)
        return proj.StartRendering()

    def get_render_job_status(self, job_id: str) -> Dict[str, Any]:
        """Returns the render progress and status of a job."""
        proj = self.get_current_project()
        if not proj:
            return {"JobStatus": "Disconnected"}
        return proj.GetRenderJobStatus(job_id)

    # -------------------------------------------------------------
    # DaVinci Resolve Studio Neural Engine & Advanced Features
    # -------------------------------------------------------------

    def apply_studio_super_scale(
        self,
        timeline_item: Any,
        multiplier: int = 2,
        noise_reduction: str = "Medium",
        sharpness: str = "Medium",
    ) -> bool:
        """
        Enables DaVinci Neural Engine Super Scale on a clip (2x, 3x, or 4x).
        Enhances 1080p action cam footage up to 4K UHD with AI edge reconstruction.
        """
        try:
            timeline_item.SetProperty("Super Scale", int(multiplier))
            timeline_item.SetProperty("SuperScale Noise Reduction", noise_reduction)
            timeline_item.SetProperty("SuperScale Sharpness", sharpness)
            logger.info(f"Applied Neural Super Scale {multiplier}x to clip {timeline_item.GetName()}")
            return True
        except Exception as e:
            logger.warning(f"Super Scale application failed: {e}")
            return False

    def apply_studio_speed_warp(self, timeline_item: Any) -> bool:
        """
        Configures DaVinci Neural Engine Speed Warp motion-estimated retiming
        for ultra-smooth slow motion on 60/100/120fps action clips.
        Resolve 21.x requires integer enums (RetimeProcess=3, MotionEstimation=4).
        """
        try:
            ok1 = timeline_item.SetProperty("RetimeProcess", 3)       # Optical Flow
            ok2 = timeline_item.SetProperty("MotionEstimation", 4)    # Speed Warp
            logger.info(f"Applied Neural Speed Warp retiming to clip {timeline_item.GetName()}")
            return bool(ok1 and ok2)
        except Exception as e:
            logger.warning(f"Speed Warp application failed: {e}")
            return False

    @staticmethod
    def normalize_lut_path(lut_path: str) -> str:
        """
        DaVinci Resolve's TimelineItem.SetLUT() requires a path relative to Resolve's
        Support/LUT directory (e.g. 'DJI/DJI OSMO Action 4 D-Log M to Rec.709 V1.cube').
        """
        norm = lut_path.replace("\\", "/")
        marker = "/Support/LUT/"
        if marker in norm:
            return norm.split(marker, 1)[1]
        return norm

    def clear_timeline_tracks(self, timeline: Any) -> int:
        """
        Clears all clips from EVERY video and audio track on the timeline.
        Prevents orphan audio clips from pushing newly appended video downstream.
        """
        cleared = 0
        for track_type in ("video", "audio"):
            cnt = timeline.GetTrackCount(track_type) or 0
            for t_idx in range(1, cnt + 1):
                items = timeline.GetItemListInTrack(track_type, t_idx) or []
                if items:
                    timeline.DeleteClips(items, False)
                    cleared += len(items)
        return cleared

    def apply_color_grade(
        self,
        timeline_item: Any,
        lut_path: Optional[str] = None,
        cdl: Optional[Dict[str, str]] = None,
        node_index: int = 1,
    ) -> bool:
        """Applies a normalized LUT and/or CDL grade (Slope/Offset/Power/Saturation) to a clip."""
        ok = True
        if lut_path:
            ok = bool(timeline_item.SetLUT(node_index, self.normalize_lut_path(lut_path))) and ok
        if cdl:
            payload = {"NodeIndex": str(node_index), **cdl}
            ok = bool(timeline_item.SetCDL(payload)) and ok
        return ok

    def insert_fusion_text_plus(
        self,
        timeline: Any,
        text: str,
        fps: float = 100.0,
        at_end: bool = True,
    ) -> Any:
        """Inserts a Fusion Text+ title at the timeline end (or current playhead) and sets StyledText."""
        if at_end:
            end_frame = int(timeline.GetEndFrame())
            total_secs = int(end_frame // fps)
            ff = int(end_frame % fps)
            hh = total_secs // 3600
            mm = (total_secs % 3600) // 60
            ss = total_secs % 60
            timeline.SetCurrentTimecode(f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}")
        title_item = timeline.InsertFusionTitleIntoTimeline("Text+")
        if title_item:
            comp = title_item.GetFusionCompByIndex(1)
            if comp:
                tools = comp.GetToolList(False, "TextPlus") or {}
                for tool in tools.values():
                    tool.SetInput("StyledText", text)
        return title_item

    def save_project(self) -> bool:
        """Saves the currently open project in DaVinci Resolve."""
        if self._project_manager:
            return bool(self._project_manager.SaveProject())
        return False

    def append_audio_clips(
        self,
        timeline: Any,
        audio_entries: List[Dict[str, Any]],
        bin_name: str = "03 Audio & SFX",
    ) -> int:
        """
        Imports audio files into the Media Pool and appends them to specified audio tracks.
        Each entry: {"path": str, "track_index": int, "record_frame": int, "start_frame": Optional[float], "end_frame": Optional[float]}
        """
        mp = self.get_media_pool()
        proj = self.get_current_project()
        if not mp or not proj:
            return 0
        proj.SetCurrentTimeline(timeline)

        # Ensure enough audio tracks exist
        max_track = max((int(e.get("track_index", 1)) for e in audio_entries), default=1)
        while (timeline.GetTrackCount("audio") or 0) < max_track:
            timeline.AddTrack("audio")

        # Locate or create audio bin
        root = mp.GetRootFolder()
        target_bin = root
        for sub in (root.GetSubFolderList() or []):
            if sub.GetName() == bin_name:
                target_bin = sub
                break
        if target_bin == root:
            created = mp.AddSubFolder(root, bin_name)
            if created:
                target_bin = created
        mp.SetCurrentFolder(target_bin)

        appended_count = 0
        imported_cache: Dict[str, Any] = {}
        for entry in audio_entries:
            audio_path = os.path.normpath(entry["path"])
            if not os.path.exists(audio_path):
                logger.warning(f"Audio file missing: {audio_path}")
                continue
            if audio_path not in imported_cache:
                existing = self.find_media_item_by_name(os.path.basename(audio_path))
                if existing:
                    imported_cache[audio_path] = existing
                else:
                    res = mp.ImportMedia([audio_path])
                    if res:
                        imported_cache[audio_path] = res[0]
            mpi = imported_cache.get(audio_path)
            if not mpi:
                continue

            clip_info: Dict[str, Any] = {
                "mediaPoolItem": mpi,
                "mediaType": 2,
                "trackIndex": int(entry.get("track_index", 1)),
                "recordFrame": float(entry.get("record_frame", timeline.GetStartFrame())),
            }
            if entry.get("start_frame") is not None:
                clip_info["startFrame"] = float(entry["start_frame"])
            if entry.get("end_frame") is not None:
                clip_info["endFrame"] = float(entry["end_frame"])

            res = mp.AppendToTimeline([clip_info])
            if res:
                appended_count += len(res)
        return appended_count

    def render_timeline(
        self,
        timeline: Any,
        target_dir: str,
        custom_name: str,
        preset_name: str = "YouTube - 1080p",
        wait: bool = True,
        timeout_seconds: int = 300,
    ) -> Dict[str, Any]:
        """Queues and renders a specific timeline using a Resolve Deliver preset."""
        proj = self.get_current_project()
        if not proj:
            raise RuntimeError("Resolve is not connected.")
        proj.SetCurrentTimeline(timeline)
        os.makedirs(target_dir, exist_ok=True)
        if preset_name in (proj.GetRenderPresetList() or []):
            proj.LoadRenderPreset(preset_name)
        proj.SetRenderSettings({
            "SelectAllFrames": True,
            "TargetDir": os.path.normpath(target_dir),
            "CustomName": custom_name,
        })
        job_id = proj.AddRenderJob()
        self.save_project()
        proj.StartRendering([job_id])
        if not wait:
            return {"job_id": job_id, "JobStatus": "Rendering"}

        start_t = time.time()
        while time.time() - start_t < timeout_seconds:
            st = proj.GetRenderJobStatus(job_id) or {}
            status = st.get("JobStatus")
            if status in ("Complete", "Failed", "Cancelled"):
                return {"job_id": job_id, **st}
            time.sleep(3)
        return {"job_id": job_id, "JobStatus": "Timeout"}

    def apply_studio_depth_map(self, timeline_item: Any) -> bool:
        """
        Inserts a 3D Depth Map ResolveFX node into the clip's color graph
        for atmospheric fog, depth-of-field blur, and depth isolation.
        """
        try:
            effect = timeline_item.AddEffect("ResolveFX", "com.blackmagicdesign.resolvefx.depthmap")
            logger.info(f"Added 3D Depth Map ResolveFX to clip {timeline_item.GetName()}")
            return effect is not None
        except Exception as e:
            logger.warning(f"3D Depth Map node insertion failed: {e}")
            return False

    def set_track_locking(
        self,
        timeline: Any,
        track_type: str = "video",
        track_index: int = 1,
        locked: bool = True,
    ) -> bool:
        """Locks or unlocks a video or audio track for bin locking / multi-user safety."""
        try:
            return timeline.SetTrackLock(track_type, track_index, locked)
        except Exception as e:
            logger.warning(f"SetTrackLock error: {e}")
            return False

    def setup_studio_collaboration(self, live_mode: bool = True) -> bool:
        """Configures multi-user project collaboration and timeline bin locking."""
        proj = self.get_current_project()
        if not proj:
            return False
        try:
            mode_str = "1" if live_mode else "0"
            proj.SetSetting("liveCollaborationMode", mode_str)
            logger.info(f"Set project live collaboration mode to {mode_str}")
            return True
        except Exception as e:
            logger.warning(f"Collaboration setup error: {e}")
            return False
