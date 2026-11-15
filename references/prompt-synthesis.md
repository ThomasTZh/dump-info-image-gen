# Prompt Synthesis

Read this when converting a validated state and visibility ledger into the final image prompt.

## Principle

The prompt is a rendering instruction for one camera. It describes what the camera sees, in the order a viewer reads it. It does not summarize the state, explain the dump, or list what is hidden.

## Assembly Order

Use this order unless the platform needs a different shape:

1. **Medium and dominant read.** Photoreal still life, cinematic environmental portrait, illustrated plate, product photograph. One clause.
2. **Camera and composition.** Height, angle, lens, shot scale, subject placement, occupancy, focus.
3. **Primary subject.** Visible silhouette, proportion, component hierarchy, material, finish, condition, pose.
4. **Scale proof.** A familiar anchor or a measured frame ratio.
5. **Secondary subjects and environment.** Supporting entities, layout, depth layers, occluders, atmosphere.
6. **Light.** Source direction, quality, shadows, bounce, rim, exposure behavior.
7. **Color and finish.** Palette, saturation, contrast, grain, medium-specific finish.
8. **Constraints.** Exact text, reference-image invariants, platform parameters.
9. **Negative prompt.** Likely failures and likely invented hidden detail.

## State To Prompt Mapping

| State field | Prompt use |
| --- | --- |
| `visual_thesis` | Controls which details get space; may become the opening clause |
| `style` / `color_finish.medium` | Opening medium clause |
| `camera` | Explicit camera sentence: height, angle, lens, distance, framing, focus |
| `scale_anchors` | Objects that prove scale |
| `entities[].geometry` | Silhouette and proportion, not a component inventory |
| `entities[].materials` / `finish` | Surface words: matte, patinated, smoked, salt-pitted |
| `entities[].features` with `visible` | Concrete visible details |
| `entities[].features` with `partial` | Visible portion plus the occluder or crop |
| `entities[].features` with `suggest` | Only the visible cue |
| `environment` | Location, depth, atmosphere, absences |
| `lighting` | Key, fill, rim, shadow behavior |
| `color_finish` | Palette, saturation, contrast, grain |
| `constraints.must_include` | Required visible elements |
| `constraints.must_avoid` | Negative prompt or absence rules |
| `constraints.exact_text` | Quoted text and placement |
| `assumptions` | Do not state; they are already baked into the chosen view |
| `conflicts` | Do not mention; the state has resolved them |
| `ignored` | Do not mention |

## Phrasing Visible Detail

Use concrete nouns and visible adjectives. Prefer one precise detail over three generic ones.

Weak:

```text
An ancient, mysterious, highly detailed tideclock with an ornate brass body and intricate mechanisms.
```

Strong:

```text
A 0.8-meter tideclock in oxidized brass, its bezel edges polished by handling, the recesses salt-pitted; a smoked-glass front dome reflects a thin line of lamp light.
```

The strong version gives size, material, condition, and a visible light behavior. It does not explain the object's history.

## Phrasing Partial Visibility

Describe the visible portion and the reason it stops:

- "partly hidden behind the lamp"
- "cut by the left frame edge"
- "softened by the smoked glass"
- "foreshortened at this angle"
- "lost in the shadow under the base"

Do not complete the hidden portion. Do not say "you can imagine the rest" or "the rest is obscured" unless the occlusion itself matters.

## Phrasing Hidden And Off-Frame Detail

Default: leave it out.

Use a negative constraint only when the model is likely to invent it:

- A rear mechanism on a front view: `no rear winding key`.
- An interior on a sealed object: `no visible internal mechanism`.
- A second wing that is off-frame but strongly implied: `no second wing entering frame`.
- Text that does not exist: `no readable text`.

Do not put hidden detail in the positive prompt as a tease. "The rear key is not visible" is still a description of a rear key and can prime the model to show it.

If the hidden detail has a legitimate cue, describe the cue and stop:

- "a low bulge breaks the left silhouette"
- "a thin shadow falls across the table behind the base"
- "a blurred second ring shows through the smoked glass"

## Visual Thesis

Choose one priority. A prompt can carry a subject, an action, and a mood; it cannot give equal weight to a mechanism, a history, a costume, a background, and a logo.

If the dump emphasizes ten details, rank them:

1. What makes the subject recognizable.
2. What proves scale or material.
3. What creates the intended feeling.
4. What the viewer can discover on a second look.

Everything else stays in the state.

## Camera And Composition Language

Use explicit, renderable terms:

- "camera at chest height, 1.2 m above the floor"
- "three-quarter front-left view, 50mm lens"
- "camera tilted down about 20 degrees"
- "subject centered, occupying two-thirds of the frame height"
- "shallow depth of field, focus on the front dome"
- "wide 3:2 frame with clean space above"

Avoid vague camera words without a mechanism: "cinematic angle", "dynamic perspective", "interesting composition".

## Scale

A number in the prompt is weaker than a comparison in the frame.

- "0.8 meters tall" is useful but abstract.
- "roughly waist-high against the table edge" is visible.
- "five small figures at the base" proves a giant object.
- "fills four-fifths of the frame" proves dominance.

Use one scale strategy, not three competing ones.

## Material And Light

Materials are read through light. Pair them:

- "matte, dry, salt-pitted brass" reads differently from "polished brass."
- "smoked glass with a faint salt film, catching a thin lamp reflection" is renderable.
- "wet stone with pooled highlights and dark seams" is renderable.

Light must be specific:

- "warm oil-lamp key from frame upper right, soft falloff"
- "cool storm light through a rain-streaked window behind the subject"
- "thin rim light along the left bezel"
- "soft contact shadow under the base"

If light is flat and frontal, say so. "Soft ambient light with minimal shadow" is a legitimate choice.

## Color And Finish

Use a small palette and a finish behavior:

- "muted brass, smoke gray, sea green, amber highlights"
- "low saturation, medium contrast, fine film grain"
- "clean digital plate, crisp edges, no grain"

Do not list every color in the dump. Choose the three or four that carry the image.

## Exact Text

If text must be readable:

- Quote it exactly.
- State where it appears and how large it is.
- State whether it is embossed, printed, painted, or illuminated.
- Do not also say "no text".

If text must not appear, say "no readable text" or "clean unmarked surfaces" and avoid quoting any text in the prompt.

## Negative Prompt

Start from failures this view is likely to produce, not from a universal list.

- Hidden parts the model may add: rear key, interior, second wing.
- Extra objects: extra dials, people, duplicate subject.
- Material drift: glossy new brass, plastic, chrome.
- Style drift: cartoon, anime, 3D render, painterly.
- Anatomy errors if people appear.
- Text, logo, watermark.
- Composition errors: cropped subject, blocked face, subject too small.

Keep negatives specific and non-contradictory. If the positive prompt says "smoked glass", do not negate "glass". If the positive prompt quotes text, do not negate "text".

## Length And Density

- Simple object or portrait: roughly 60 to 120 words.
- Complex scene or multi-part subject: roughly 120 to 200 words.
- Platform limits override these ranges.
- If the prompt exceeds the useful length, cut secondary features, not the camera or the subject.

Density is not quality. A shorter prompt with a fixed camera, a clear subject, and consistent light beats a longer prompt with ten competing details.

## Multi-View Prompts

When one world has several views:

- Repeat the invariant dimensions, materials, colors, damage, and time of day.
- Change the camera, framing, visibility, and light interaction explicitly.
- Do not write "same as the previous image"; the model may not have it.
- Do not show a feature in one view that another view establishes as absent.
- Keep the same visual thesis across views unless the user asks for a different mood.

## Platform

Format the finished prompt for the target model. See `references/platform-profiles.md`.

- Portable: natural language plus optional `Negative:`.
- Midjourney: compact one line, `--no` terms, aspect ratio.
- Stable Diffusion, SDXL, Flux: `Positive:` and `Negative:` blocks.
- DALL-E / OpenAI: natural-language instructions, quoted text, explicit placement.

## Anti-Patterns

- **Encyclopedia prompt.** Every dumped fact appears, including hidden and non-visual material.
- **State leakage.** "The visibility ledger shows the rear key is hidden" inside the prompt.
- **Adjective pile.** "Ancient, mysterious, intricate, epic, ultra-detailed" with no visual mechanism.
- **Camera contradiction.** A front view that describes the back panel as visible.
- **Impossible light.** Warm key from the left and shadows falling left.
- **Scale drift.** "Colossal" with no anchor and a camera at eye level.
- **Text invention.** A guild mark or slogan that the dump never made readable.
- **Negative contradiction.** "No text" with a quoted inscription.
- **Unreconstructed update.** New facts appended to the old prompt instead of rebuilding.

## Final Check

- The first sentence establishes medium and dominant read.
- The camera is explicit and consistent with the visible surfaces.
- The primary subject is described with visible form, material, and scale.
- Hidden features are absent from the positive prompt.
- Light, shadow, and reflection agree.
- Negatives are specific and do not contradict the positive.
- The prompt sounds like image direction, not a state export.
