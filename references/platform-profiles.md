# Platform Profiles

Read this when the user names a target image model or asks for platform-specific formatting.

## Portable Default

Use natural-language image direction when the platform is unknown. Keep the order stable:

1. Medium and dominant read
2. Camera and composition
3. Primary visible subject
4. Scale proof
5. Environment
6. Lighting
7. Color and finish
8. Constraints and negatives

Return:

```text
Prompt: ...
Negative: ...
```

Omit `Negative:` when there is nothing specific to prevent.

## Midjourney

Prefer compact, image-dense phrasing.

- Put subject, medium, camera, and mood early.
- Keep the camera explicit; short lens and angle phrases work well.
- Use `--ar` only when aspect ratio matters.
- Keep negatives short: `--no text, logo, rear key, extra dials`.
- Avoid numbered sections, long procedural instructions, and state terminology.
- Use stylization or chaos parameters only when the user asks for variation or a strong style.

Shape:

```text
[subject and visible detail], [camera/lens], [composition], [environment], [lighting], [palette and finish] --ar 3:2 --no text, logo, rear key
```

## Stable Diffusion, SDXL, Flux

Prefer separated positive and negative prompts.

- Positive: subject first, then camera and composition, then material, environment, lighting, and finish.
- Negative: defects, unwanted additions, hidden parts likely to be invented, text or logos, style drift, anatomy errors.
- Put the most important controls early; long prompts lose weight.
- Use weights, LoRA names, embeddings, ControlNet, or model-specific tokens only when the user supplies them or explicitly asks.
- Do not invent checkpoints, LoRA names, or embedding names.

Shape:

```text
Positive: [subject], [camera and composition], [material], [environment], [lighting], [style]
Negative: [hidden parts], text, logo, watermark, extra objects, deformed anatomy, low quality, blurry, oversaturated
```

## DALL-E And OpenAI Image Models

Prefer natural language with clear constraints.

- Use complete sentences.
- Explain exact placement, crop, text, and purpose.
- Quote readable text and say where it appears.
- For edits, repeat invariants: keep identity, pose, crop, lighting direction, and perspective unless asked to change them.
- Avoid model flags such as `--ar` unless the interface supports them.
- State absence rules as natural language: "Do not include readable text, logos, or a rear winding key."

Shape:

```text
Create a [medium] image of [subject]. The camera is [camera and position]. The composition places [layout and scale]. [Visible material and detail]. Lighting comes from [direction and quality]. Use [palette and finish]. Do not include [negatives].
```

## Leonardo, Firefly, And General Web Generators

Use portable natural language plus short negatives.

- Keep the subject and camera near the start.
- Mention commercial cleanliness and safe typography space for marketing images.
- Avoid platform-specific syntax unless requested.
- Do not use public logos or protected characters unless the user supplies them.
- For product images, keep the product visible and the geometry undistorted.

## Platform Selection Rule

If the user does not name a platform, produce a portable prompt and optionally add:

```text
For Midjourney, compress this into one line and add aspect ratio and --no terms.
For Stable Diffusion or Flux, split it into Positive and Negative prompts.
```

Do not change the reconstruction when changing the platform. Only the packaging changes.
