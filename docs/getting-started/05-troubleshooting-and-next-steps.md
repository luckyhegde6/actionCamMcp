# 5. Troubleshooting and Next Steps

## Recording and card issues

### Camera says the card is too slow or cannot record

1. Stop recording and power off.
2. Back up all files before testing or formatting.
3. Confirm the card has the U3 and V30 marks.
4. Inspect the card for damage and verify the exact model number.
5. Format in-camera only after backup.
6. Repeat a 10-minute test recording and verify the copied file.
7. If errors continue, test the card's actual capacity or replace it with a model on DJI's recommended list.

### Recording stops unexpectedly

- Check free card space.
- Check battery level and camera temperature.
- Confirm the card is seated correctly.
- Test with a short clip at the intended recording settings.
- Do not assume the card is healthy simply because the camera can read its directory.

### Indoor footage flickers

- Start with 25 fps under 50 Hz lighting.
- Test the exact room and light source.
- Later, try manual shutter around 1/50 second for 25 fps.
- LED dimmers and electronic drivers can still flicker; test before filming an important event.

### Footage looks too wide or distorted

- Try a less-wide FOV option if available.
- Keep faces and important objects away from the extreme edges.
- Compare the camera's available FOV choices with the same scene.

### Walking footage looks shaky

- Slow down.
- Use shorter steps and keep elbows close.
- Avoid abrupt pans.
- Use RockSteady 3.0 as the first baseline and compare other modes only when needed.

## DaVinci Resolve issues

### Timeline frame rate is wrong or locked

Set the timeline frame rate before importing clips into an empty Media Pool. If it is already locked, create a new project with the intended frame rate and import the media there.

### Playback is slow

- Set Timeline Proxy Resolution to Half or Quarter.
- Generate proxy media for difficult-to-decode clips.
- Keep the timeline at 1080p.
- Close other GPU-heavy applications.
- Reduce heavy effects and noise reduction.

### Colours look strange

- Confirm the camera recorded Normal colour.
- Do not apply a D-Log M conversion LUT to Normal footage.
- Check that the viewer and export are being interpreted consistently.
- Learn scopes and colour management before building a custom LUT.

## Learning roadmap

| Phase | Focus | Outcome |
|---|---|---|
| 1 | Camera and recording basics | Reliable, repeatable footage |
| 2 | Composition and storytelling | Intentional shot sequences |
| 3 | Resolve fundamentals | Confident import, trim, edit, export |
| 4 | Editing and audio | Clean pacing and understandable sound |
| 5 | Colour science | Exposure, white balance, Rec.709, scopes |
| 6 | LUT development | Technical conversion and creative looks |
| 7 | Media analysis and AI | Searchable footage and assisted review |
| 8 | YouTube publishing | Strong title, thumbnail, description, chapters |

## What to practice next

Before moving to manual exposure or D-Log M, complete these three tasks:

1. Record the six-shot mini-film twice, improving the two weakest shots.
2. Import and edit it in a 1080p/25 fps Resolve project.
3. Export and review the final file on a separate player.

Then move to shutter speed, ISO, exposure compensation, and white balance as separate lessons.

## References

- [DJI Osmo Action 4 specifications](https://www.dji.com/osmo-action-4/specs)
- [DJI beginner's guide](https://support.dji.com/help/content?customId=01700008145&lang=en&paperDocType=ARTICLE&re=GB&spaceId=17)
- [DaVinci Resolve 21.1 Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21.1_Reference_Manual.pdf)
