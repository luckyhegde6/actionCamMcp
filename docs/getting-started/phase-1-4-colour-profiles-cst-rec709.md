# Phase 1.4 — Colour Profiles, CST and Rec.709

A camera capture profile, colour space/gamut, transfer function, and output standard are related but not interchangeable.

## 1. What the Action 4 records

| Profile/concept | Meaning | Guidance |
|---|---|---|
| Normal | Processed contrast/colour for convenient viewing | Use for first projects |
| D-Log M | Lower-contrast 10-bit capture designed to preserve more grading latitude | Use after exposure/WB practice; requires matching normalization |
| HLG | HDR transfer function used by some cameras and displays | Not a documented selectable Action 4 capture profile |

DJI documents 10-bit D-Log M and Normal for Action 4 capture; published specs do not list HLG as a selectable capture profile. HLG is covered here so you can recognize it in HDR footage or delivery settings elsewhere.

## 2. Colour space, gamma and Rec.709

- **Gamut/colour space:** range of colours represented.
- **Transfer function/gamma:** how brightness is encoded.
- **Rec.709:** common SDR HD video standard for conventional viewing.
- **HLG:** a transfer function for HDR systems, not a more saturated Rec.709 look.

A transform must match the actual input and intended output. Incorrect tagging or assumptions can produce wrong colour.

## 3. What CST means

CST = Color Space Transform. Resolve's CST effect converts from a specified input colour space/gamma to an output colour space/gamma. It is a technical transform, not a creative look.

Conceptually: camera input → technical normalization → creative adjustments → Rec.709 SDR output.

For Normal Action 4 footage, do not apply a D-Log M conversion. Use a Rec.709 SDR project workflow and basic correction.

For D-Log M footage, use DJI's matching D-Log M-to-Rec.709 LUT as the beginner technical conversion unless you have verified exact CST input mapping for this camera profile and Resolve version. Do not guess a generic camera gamut/gamma pair for D-Log M.

## 4. DJI LUTs: conversion vs creative look

DJI provides:
- **Osmo Action 4 D-Log M to Rec.709 vivid LUT:** technical conversion for D-Log M footage.
- **Osmo Action 4 Rec.709 to Color Grading LUTs:** creative grading LUTs designed for Rec.709 input.

Workflow:
1. Identify the recording profile from camera settings/notes.
2. Normalize D-Log M with the matching DJI conversion LUT or a verified colour-managed transform.
3. Correct exposure and white balance in a consistent pipeline.
4. Add a creative look only if desired.
5. Check scopes and export to the intended output.

**Never apply the D-Log M-to-Rec.709 conversion LUT to Normal footage.** It produces an incorrect result.

## 5. Beginner Resolve workflow

**Normal footage**
1. Use a Rec.709 SDR project/output workflow.
2. Do not add a D-Log M LUT or D-Log M CST.
3. Correct exposure and WB gently.
4. Adjust contrast/saturation conservatively.
5. Check Waveform and RGB Parade.

**D-Log M footage**
1. Confirm the clip was recorded D-Log M; do not infer only from its flat appearance.
2. Download the Action 4 D-Log M-to-Rec.709 LUT from DJI.
3. Install it in Resolve and refresh the LUT list.
4. Apply it once in a consistent node/pipeline position.
5. Review exposure/WB; a LUT does not fix poor capture exposure.
6. Make creative adjustments after technical normalization.
7. Check scopes and export SDR Rec.709.

If building a CST pipeline later, validate the input mapping against DJI technical information and compare against the official LUT. A guessed CST can be worse than the official conversion.

## 6. What about HLG?

HLG is relevant to HDR sources and HDR deliverables, not the Action 4's documented capture profile. For this beginner workflow, learn SDR Rec.709 first. Do not choose HLG output just because a clip is D-Log M. HDR monitoring, display capability, metadata and HLG output are a later topic. Rec.709 SDR and HLG HDR are not interchangeable deliverables.

## 7. Exercise

If you have only recorded Normal so far, do not simulate D-Log M by applying its LUT to Normal footage. Record one Normal clip. When ready, record a separate D-Log M clip of the same scene, import both, correct Normal manually, normalize only D-Log M with DJI's matching conversion, then compare highlight/shadow detail, noise, colour and time to finish.

## Review checklist

- [ ] I distinguish Normal from D-Log M.
- [ ] I understand HLG is not a documented Action 4 capture profile.
- [ ] Rec.709 is my initial SDR delivery target.
- [ ] I can explain what CST does.
- [ ] I never apply D-Log M conversion to Normal footage.
- [ ] I use one matching technical conversion and check scopes.

## Next

[Phase 1.5 — Media workflow and Resolve performance](phase-1-5-media-workflow-performance.md)

## Official references

- [DJI Action 4 specifications — 10-bit D-Log M](https://www.dji.com/osmo-action-4/specs)
- [DJI downloads — official D-Log M-to-Rec.709 and Rec.709 creative LUTs](https://www.dji.com/osmo-action-4/downloads)
- [Blackmagic Design — DaVinci Resolve Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinciResolveReferenceManual.pdf)
