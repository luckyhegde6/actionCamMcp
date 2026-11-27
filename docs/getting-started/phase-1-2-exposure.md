# Phase 1.2 — Exposure

Learn shutter speed, ISO, EV compensation, white balance, clipping and exposure review using short controlled tests.

## 1. Exposure controls

| Control | Meaning | Trade-off |
|---|---|---|
| Shutter | How long each frame is exposed | Faster = less light and less motion blur; slower = more blur |
| ISO | Sensor signal amplification | Higher ISO brightens but adds noise/reduces detail |
| EV | Bias to Auto exposure | Negative darkens; positive brightens |
| White balance | Neutralizes the colour of the light | Auto can shift during a clip; fixed WB is consistent in steady light |

The Action 4 has a fixed f/2.8 aperture. DJI lists video ISO 100–12800 as the camera's capability range, not a recommended everyday target.

## 2. 180-degree shutter starting points

| Frame rate | Shutter |
|---|---:|
| 25 fps | 1/50 s |
| 30 fps | 1/60 s |
| 50 fps | 1/100 s |
| 60 fps | 1/120 s |

These are starting points for natural motion blur, not rigid rules. Faster shutter looks crisp/staccato; slower shutter adds blur.

**India / 50 Hz:** Start with 25 fps and 1/50 s indoors. DJI's automatic anti-flicker guidance recommends 25/50/100 fps in 50 Hz regions. 30/60 fps can work outdoors or under tested lighting but some LEDs and dimmers may flicker. Always record a short test under the actual lights.

## 3. ISO practice

- Use the lowest ISO that gives correct exposure with the shutter you want.
- ISO 100 is a useful daylight target if exposure allows.
- Indoor scenes may need higher ISO; inspect shadows for noise.
- Do not underexpose badly and expect to recover everything in Resolve.
- Set an Auto ISO ceiling only if your firmware exposes that control.

## 4. EV compensation

In Auto exposure, try EV 0 as the baseline, -0.3/-0.7 to protect bright sky or pale surfaces, and +0.3 to lift a dark subject when the background is not already bright. Change in small steps. EV may be unavailable or have no effect in fully manual exposure.

## 5. White balance

Auto WB is convenient when moving between locations but may change colour mid-clip. For steady lighting, test fixed values:
- Daylight: approximately 5200–5600 K.
- Warm indoor/tungsten: approximately 3000–3500 K.
- Mixed LEDs: test visually; Kelvin alone may not remove green/magenta tint.

These are estimates, not universal presets. Keep the camera's front colour-temperature sensor unobstructed. Auto WB can be more practical when moving between shade and sun.

## 6. Clipping and exposure review

Highlight clipping is featureless white; crushed shadows lose texture and become featureless black. Protect important detail (clouds, faces, pale objects), not every specular reflection.

Use any overexposure warning only if it is actually available in the current firmware/mode; do not assume every mode has zebras or a waveform. In Resolve:
1. Open Color page and enable Waveform and RGB Parade.
2. Inspect sky, windows, white objects, and dark areas.
3. Look for signal pressed against the top/bottom of the scale.
4. Check the image as well as the scopes. Scopes inform judgement; they do not replace it.

## 7. Exercise — one scene, four exposures

Record four 8–10 second clips of the same static subject:
1. Auto exposure, EV 0, Auto WB.
2. Auto exposure, EV -0.7, Auto WB.
3. Manual shutter 1/50 at 25 fps, ISO Auto if available.
4. Manual shutter 1/50, fixed WB selected for the light.

Keep framing and lighting unchanged. Compare brightness, motion blur, noise and colour. Change one variable at a time.

## Review checklist

- [ ] Important highlights retain texture.
- [ ] Subject is not unintentionally too dark.
- [ ] Shadows are not crushed without intent.
- [ ] ISO is not unnecessarily high.
- [ ] Motion blur looks natural.
- [ ] White balance is consistent in steady lighting.
- [ ] Indoor test has no visible flicker/banding.
- [ ] I can explain which setting caused each difference.

## Next

[Phase 1.3 — Frame rates and slow motion](phase-1-3-frame-rates-slow-motion.md)

## Official references

- [DJI Action 4 specifications — ISO, shutter and recording modes](https://www.dji.com/osmo-action-4/specs)
- [DJI Support — manual shutter and ISO controls](https://repair.dji.com/help/content?customId=01700006934&lang=en&paperDocType=ARTICLE&re=US&spaceId=17)
- [DJI Support — automatic anti-flicker guidance](https://repair.dji.com/help/content?customId=01700008288&lang=en&paperDocType=ARTICLE&re=US&spaceId=17)
