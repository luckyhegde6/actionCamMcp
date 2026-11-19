# DJI Osmo Action 4 — Beginner Getting Started

Welcome to the IlluMen_Dev Video Production Lab. This guide takes you from preparing your microSD card to recording, reviewing and editing your first short sequence.

## Your starting setup

| Item | Current setup |
|---|---|
| Camera | DJI Osmo Action 4 |
| Firmware | Updated |
| microSD | SanDisk Extreme, 128 GB, V30 |
| Mounting | Handheld |
| Audio | Built-in camera microphones |
| Recording target | 1080p, 25 fps |
| Colour | Normal |
| Editing | DaVinci Resolve Studio 21.2 |
| Computer | Windows 11, 16 GB RAM, GTX 1650 4 GB |
| Lighting environment | India, 50 Hz mains |

## Learning path

1. [Memory card and recording workflow](01-memory-card-and-recording.md)
2. [Beginner camera configuration](02-camera-configuration.md)
3. [Handheld shooting and first exercise](03-handheld-shooting-exercise.md)
4. [DaVinci Resolve setup and first project](04-davinci-resolve-first-project.md)
5. [Troubleshooting and next steps](05-troubleshooting-and-next-steps.md)

## Phase 1 — Camera mastery

| Phase | Learn | Guide |
|---|---|---|
| 1.1 | Camera setup, storage, safe recording and basic handheld technique | [Getting Started and first exercise](README.md) |
| 1.2 | Shutter, ISO, EV, white balance, clipping and exposure review | [Exposure](phase-1-2-exposure.md) |
| 1.3 | 25/30/50/60 fps, 50 Hz flicker considerations and slow motion | [Frame rates and slow motion](phase-1-3-frame-rates-slow-motion.md) |
| 1.4 | Normal, D-Log M, HLG, CST and Rec.709 | [Colour profiles and transforms](phase-1-4-colour-profiles-cst-rec709.md) |
| 1.5 | Metadata, previews, proxies, clipping checks and Resolve performance | [Media workflow and performance](phase-1-5-media-workflow-performance.md) |

**Recommended sequence:** complete each lesson in order. Keep 1080p/25 fps and Normal colour as the everyday baseline while learning. The 30/60 fps exercises are useful comparisons, but test lighting carefully in India's 50 Hz environment.

## Your first six-shot mini-story

A short video becomes easier to understand when each shot has a purpose. Record the six shots below in order; aim for roughly 8–12 seconds per clip and hold the camera steady briefly before and after movement.

| Shot | What to capture | Why it matters |
|---|---|---|
| 1. Establishing | A wide view of the location | Answers “Where are we?” |
| 2. Detail | A close view of an interesting object or texture | Shows what matters |
| 3. Movement | One slow, controlled pan or camera move | Adds visual energy |
| 4. Action | A person or object doing something | Shows something happening |
| 5. Point of view | A natural eye-level or chest-level perspective | Places the viewer in the scene |
| 6. Closing | A final wide shot or meaningful detail | Gives the sequence an ending |

See the [handheld shooting exercise](03-handheld-shooting-exercise.md) for shot-by-shot instructions and review guidance.

## First-video workflow

Prepare → Configure → Record → Review exposure and motion → Copy and verify → Inspect metadata → Edit → Export → Review

## Beginner safety and quality rules

- Do not apply a D-Log M conversion LUT to footage recorded in Normal colour.
- HLG is not a documented selectable Action 4 capture profile; learn Rec.709 SDR first.
- Keep original camera files unchanged and maintain a verified backup before formatting the card.
- Start with 1080p/25 fps. Learn exposure and composition before adopting advanced profiles.
- Camera options vary by firmware and selected mode. Confirm the current on-camera options and DJI documentation.

## Resolve companion guide

For installation, project setup, file-based Action 4 integration, basic editing, LUT installation and beginner export presets, see [DaVinci Resolve — Setup and First Project](04-davinci-resolve-first-project.md) and the [GitHub Wiki guide](https://github.com/luckyhegde6/actionCamMcp/wiki/DaVinci-Resolve).

## Official references

- [DJI Osmo Action 4 specifications and recommended microSD cards](https://www.dji.com/osmo-action-4/specs)
- [DJI Osmo Action 4 downloads and user manual](https://www.dji.com/osmo-action-4/downloads)
- [DJI Support — manual shutter and ISO](https://repair.dji.com/help/content?customId=01700006934&lang=en&paperDocType=ARTICLE&re=US&spaceId=17)
- [DJI Support — automatic anti-flicker guidance](https://repair.dji.com/help/content?customId=01700008288&lang=en&paperDocType=ARTICLE&re=US&spaceId=17)
- [Blackmagic Design — DaVinci Resolve Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinciResolveReferenceManual.pdf)
