---
name: speech-cleanup-and-subtitles
description: "Automated dialogue audio cleanup, Fairlight Voice Isolation, silence removal, 9:16 vertical Smart Reframe, and animated subtitle generation."
tags: [speech-cleanup, voice-isolation, subtitles, long-to-shorts, fairlight, resolve-studio]
author: "ActionCam MCP / ChatCut Compatible"
version: "1.0.0"
---

# Speech Cleanup, Long Video to Shorts & Dynamic Captions

This skill playbook automates dialogue enhancement, silence trimming, automatic subtitle generation, and converting long horizontal footage into engaging 9:16 vertical shorts.

---

## 1. Flow Pipeline

1. **Fairlight Voice Isolation**:
   - Neural Engine voice isolation eliminates background wind noise, motor rumble, and HVAC hum:
   ```python
   # On timeline track or audio clip
   timeline_item.SetProperty("Voice Isolation", "1")
   timeline_item.SetProperty("Voice Isolation Level", 85)
   ```
2. **Silence Removal**:
   - Analyzes audio track transients and removes pauses greater than 0.4 seconds.
3. **Smart Reframe (16:9 to 9:16 Vertical)**:
   - Sets timeline resolution to `1080x1920`.
   - Invokes DaVinci Resolve Neural Engine **Smart Reframe** on the video track to automatically track the speaking person or action subject in the center of the vertical frame:
   ```python
   timeline_item.SetProperty("Smart Reframe", "Auto")
   ```
4. **Auto-Captions & Subtitle Track**:
   - Generates synchronized subtitles using Resolve Studio's speech-to-text engine:
   - Places word-by-word highlights and dynamic kinetic typography on Subtitle Track 1.
5. **Video Translation / Multilingual Track**:
   - Generates secondary dubbed or translated audio tracks (Track A2) with background music auto-ducking (-12dB).

