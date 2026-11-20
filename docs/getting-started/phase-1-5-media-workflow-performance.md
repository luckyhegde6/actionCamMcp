# Phase 1.5 — Media Workflow, Metadata, Proxies and Quality Checks

A repeatable path from Action 4 microSD to a responsive Resolve project. Target machine: Windows 11, 16 GB RAM, GTX 1650 4 GB, preferred 1080p timeline.

## 1. Project folder structure

~~~text
Action4_Project_Name/
├── 00_Card_Manifest/
├── 01_Originals/
├── 02_Audio/
├── 03_Resolve_Project/
├── 04_Proxies/
├── 05_Stills_Thumbnails/
├── 06_LUTs/
├── 07_Exports/
└── 08_Review_Notes/
~~~

Keep the card's folder structure where practical. Copy, do not move, source media. Do not format the card until the copy is verified and important footage has a second backup.

## 2. Copy and verify

1. Stop recording and power off before removing the card.
2. Use a reliable reader.
3. Copy the complete DCIM/media folder to 01_Originals; do not rename originals during copy.
4. Compare file counts and total size.
5. Open samples from the beginning, middle and end.
6. For important footage, make a second copy on another physical drive before formatting.

For stronger verification, compare SHA-256 hashes of source and destination files. Keep originals untouched.

## 3. Metadata to inspect

| Field | Why it matters |
|---|---|
| Filename/duration | Identify clips and organize |
| Resolution/aspect ratio | Confirm source dimensions |
| Frame rate | Detect 25/30/50/60 and slow-motion sources |
| Codec/container/bitrate | Understand decode and storage load |
| Audio sample rate/channels | Confirm audio tracks |
| Creation timestamp | Reconstruct recording order |
| Colour/profile notes | Distinguish Normal and D-Log M; generic metadata may not reliably identify profile |

Use Resolve Media Pool metadata columns/Clip Attributes first. MediaInfo or FFprobe are optional external tools. Keep a shoot note/bin label for Normal vs D-Log M rather than assuming a metadata tag always identifies it.

Optional FFprobe command (reads metadata; does not modify the file):

~~~powershell
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate,bit_rate,pix_fmt,color_space,color_transfer,color_primaries -show_entries format=duration,size,bit_rate -of json "clip.mp4"
~~~

Treat missing/unknown colour tags as unknown, not proof of a profile.

## 4. Previews and contact sheets

Use Resolve's source viewer and thumbnails for first review. When clip counts grow, generate still thumbnails/contact sheets and store them separately from camera originals. Name previews consistently with source clip names. Add a note for subject, best time range, audio quality and exposure/flicker issue. A contact sheet is a browsing aid, not a replacement for watching motion and listening to audio.

## 5. Proxies

A proxy is a smaller/easier-to-decode copy used while editing. The original remains the source for final-quality rendering when proxy settings are configured correctly.

For GTX 1650 4 GB:
- Start with original 1080p footage; proxies may not be needed.
- For 4K/HEVC or stuttering footage, try Half or Quarter resolution proxies.
- DNxHR LB is a practical edit-friendly proxy format to test on Windows HD timelines; it uses disk space, so monitor free space.
- Store proxies in 04_Proxies or a dedicated proxy location, separate from originals.
- Generate via Resolve's Media Pool proxy workflow and confirm proxy playback.
- Keep paths organized and relinkable. Never delete originals after proxy creation.

Proxy media creates alternate files. Timeline Proxy Resolution lowers viewer/playback resolution without creating files. They are different features.

## 6. Resolve performance workflow

1. Set timeline resolution/frame rate before editing.
2. Keep source originals on a fast local drive where possible.
3. Set cache/proxy locations to a drive with sufficient free space.
4. Try Playback → Timeline Proxy Resolution → Half, then Quarter.
5. Generate proxies for only difficult clips first.
6. Use render cache for effects-heavy sections.
7. Close unnecessary browser tabs and GPU-heavy applications.
8. Avoid heavy temporal noise reduction, multiple OFX effects and complex Fusion compositions in the first project.
9. If GPU memory errors appear, reduce viewer/timeline load and disable demanding effects before changing GPU settings.

Confirm GPU detection in Resolve Preferences. Do not force a GPU mode Resolve does not report as supported.

## 7. Exposure/clipping review in Resolve

For representative frames from every lighting condition:
1. Open Color page.
2. Enable Waveform and RGB Parade scopes.
3. Inspect sky, windows, white objects and reflections.
4. Inspect shadows for crushed detail/noise.
5. Compare scope readings with the image.
6. Note clips with clipping, flicker, underexposure or changing WB.

Scopes reveal signal levels; they cannot restore highlight detail clipped during capture. Correct exposure on the next take.

## 8. Clip review labels

| Status | Meaning |
|---|---|
| KEEP | Technically sound and useful |
| REVIEW | Usable but needs closer inspection |
| RE-SHOOT | Important content compromised |
| REJECT | Accidental, corrupt or unusable |

Review focus, stabilization artefacts, exposure/clipping, flicker, WB shifts, wind/handling noise, audio clipping/channels and corrupt files.

## 9. Hands-on ingest exercise

1. Create a project folder using the structure above.
2. Copy 5–10 clips to 01_Originals.
3. Verify file count, total size and playback.
4. Inspect dimensions, frame rate, codec, duration and audio.
5. Import and organize bins by shot type.
6. Generate proxies for one demanding clip only.
7. Compare playback with proxy on/off.
8. Review one bright and one dark scene with Waveform/RGB Parade.
9. Record a short note on issues to fix next time.

## Completion checklist

- [ ] Originals copied without renaming.
- [ ] File count/size checked and sample clips play.
- [ ] Second backup made before formatting important footage.
- [ ] Metadata inspected.
- [ ] Normal/D-Log M profile noted from capture settings.
- [ ] Previews/contact sheets stored separately.
- [ ] Proxies stored separately and only created where useful.
- [ ] Resolve playback is adequate for editing.
- [ ] Exposure/clipping and audio review completed.
- [ ] Original camera files remain untouched.

## Official references

- [DJI Action 4 specifications](https://www.dji.com/osmo-action-4/specs)
- [Blackmagic Design — DaVinci Resolve Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinciResolveReferenceManual.pdf)
- [FFmpeg FFprobe documentation](https://ffmpeg.org/ffprobe.html)
- [MediaInfo](https://mediaarea.net/en/MediaInfo)
