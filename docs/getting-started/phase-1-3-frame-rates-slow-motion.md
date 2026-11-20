# Phase 1.3 — Frame Rates and Slow Motion

Frame rate is the number of images recorded each second. It changes motion cadence, storage load and how clips behave on a timeline.

## 1. Choose a frame rate

| Capture | Typical use | On a 25 fps timeline |
|---|---|---|
| 25 fps | Everyday, dialogue, travel, indoor 50 Hz environments | Normal speed |
| 30 fps | 30 fps delivery or tested lighting | Needs a frame-rate decision/conform |
| 50 fps | Smooth action, half-speed option | 2× slower when conformed to 25 |
| 60 fps | Fast action or slow motion, preferably daylight/tested light | 2.4× slower when conformed to 25 |

The Action 4 supports 25/30/50/60 fps at 1080p, 2.7K and 4K in supported standard-video combinations. Exact availability depends on aspect ratio, stabilization and mode; consult DJI's table.

## 2. India / 50 Hz lighting

- Use 25 fps as the everyday default.
- Use 50 fps when you may want half-speed or need to capture fast action.
- Use 30/60 fps in daylight or under lighting you have tested.
- DJI's anti-flicker support is automatic and recommends 25/50/100 fps in 50 Hz regions.

50 Hz mains does not guarantee every LED flickers at 50 Hz. Drivers and dimmers vary. Test the exact room.

## 3. Shutter guide

| Frame rate | Approximate shutter |
|---|---:|
| 25 | 1/50 s |
| 30 | 1/60 s |
| 50 | 1/100 s |
| 60 | 1/120 s |

These follow the approximate 180-degree shutter guideline. High-frame-rate capture needs more light to maintain the same shutter rule.

## 4. Slow-motion maths

When played at 25 fps:
- 50 capture → 2× slower.
- 60 capture → 2.4× slower.
- 100 capture → 4× slower.
- 120 capture → 4.8× slower.
- 200 capture → 8× slower.
- 240 capture → 9.6× slower.

DJI specifies dedicated Slow Motion up to 4× at 4K/120 and 2.7K/120, and 8× at 1080p/240. Check exact on-camera options. DJI specifies electronic stabilization is not supported in Slow Motion mode; plan handheld movement accordingly.

## 5. Standard Video or Slow Motion mode?

**Standard Video at 50/60 fps** lets you choose later whether to keep normal speed or slow only a section. **Dedicated Slow Motion** creates a slow-motion result in-camera, but some stabilization options are unavailable.

For the first comparison, record standard video at 50 fps rather than immediately switching to dedicated Slow Motion.

## 6. Exercise — same action at four rates

Record the same repeatable action (pour water, wave a hand, spin a wheel) at 25, 30, 50 and 60 fps. Keep position, framing and light similar. Use the shutter table when practical; avoid 30/60 fps tests under untested indoor LEDs.

In Resolve, compare motion, flicker, blur, file size and playback. On a 25 fps project, use Clip Attributes / Video Frame Rate to interpret a high-rate clip at 25 fps, or use Change Clip Speed / Retime Controls for only the section you want slowed. Do not change the entire project frame rate to slow one shot.

## Review checklist

- [ ] I can explain why I chose each rate.
- [ ] 50 fps conforms to 2× slow motion on a 25 fps timeline.
- [ ] 60 fps is checked for cadence and flicker.
- [ ] I understand high frame rates need more light for the same shutter.
- [ ] I checked stabilization availability in the selected mode.

## Next

[Phase 1.4 — Colour profiles, CST and Rec.709](phase-1-4-colour-profiles-cst-rec709.md)

## Official references

- [DJI Action 4 specifications — frame rates and slow motion](https://www.dji.com/osmo-action-4/specs)
- [DJI Action 4 FAQ](https://www.dji.com/osmo-action-4/faq)
- [DJI Support — anti-flicker guidance](https://repair.dji.com/help/content?customId=01700008288&lang=en&paperDocType=ARTICLE&re=US&spaceId=17)
