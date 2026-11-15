# Camera And Visibility

Read this when choosing a view, computing what is visible, or resolving why a detail should not appear in the prompt.

## Principle

The camera is part of the reconstruction. Changing the camera changes the image more than changing adjectives. Fix the world, then derive the view.

## Camera Station

Record these fields in the state:

| Field | Meaning | Example |
| --- | --- | --- |
| view_id | Short name for reuse | `front-left-three-quarter` |
| height | Camera height above the ground plane | `1.2 m` |
| distance | Camera to subject distance | `2.5 m` |
| azimuth_deg | Horizontal angle from the subject's front, positive toward the subject's right | `-35` |
| elevation_deg | Vertical angle, positive above the horizon, negative below | `8` |
| lens | Focal length equivalent, or field of view | `50mm` |
| shot_scale | How much of the subject is in frame | `full object with context` |
| framing | Placement and occupancy | `subject centered, 65% of frame height` |
| focus | What is sharp | `front dome` |
| depth_of_field | Aperture behavior | `f/2.8, shallow` |
| aspect_ratio | Output shape | `3:2` |

Azimuth convention matters. State it once and keep it: `0` is the front, `-90` is the subject's left, `+90` is its right, `180` is the rear. Elevation `0` is level with the subject's center; positive is above.

## Angle Presets

| Need | Camera | Visibility |
| --- | --- | --- |
| Iconic, symmetrical read | Front, eye level, moderate distance | Front surface; left and right compressed |
| Show form and volume | Three-quarter, slightly above | Front plus one side plus top edge |
| Emphasize silhouette | Profile, level, long lens | One side; strong outline; far side hidden |
| Threat or dominance | Low angle, close, wide lens | Underside, front, no top |
| Layout or map logic | High angle or top-down | Top surfaces; fronts compressed; verticals hidden |
| Intimacy | Eye level, close, normal lens | Face and near shoulder; background soft |
| Scale | Low or level, distant, telephoto | Subject mass plus small anchors |
| Detail | Macro, close | One surface zone; context absent |
| Mystery | Rear three-quarter or obstructed view | Back and side; identity cues only |
| User-specified | Use it exactly | Recompute from that station |

Do not default to a front view when the dump's defining feature is on the side or rear. Do not choose a view that hides the only feature that makes the subject recognizable unless the brief is explicitly about mystery.

## Surface Visibility

A surface is visible only if all four gates pass:

1. **In frame.** The feature is inside the camera frustum at the chosen aspect ratio and shot scale.
2. **Faces the camera.** The surface normal points toward the camera. At a grazing angle the surface is visible but foreshortened; treat it as partial.
3. **Unoccluded.** An opaque object closer to the camera does not block the line of sight. Transparent or translucent occluders change this: glass reveals with distortion, haze reveals with reduced contrast, smoke may hide completely.
4. **Legible.** The feature is large enough, contrasting enough, and sharp enough to be read at this distance. A dark detail in shadow may be geometrically visible but not readable.

Approximate facing by azimuth:

| Azimuth | Surfaces facing the camera |
| --- | --- |
| `-180` to `-90` | Rear and subject-left |
| `-90` to `0` | Front and subject-left |
| `0` to `+90` | Front and subject-right |
| `+90` to `+180` | Rear and subject-right |

Elevation adds top surfaces when positive and underside surfaces when negative. At high elevation, front surfaces foreshorten; at low elevation, tops disappear and undersides grow.

## Visibility States

| State | Meaning | Prompt action |
| --- | --- | --- |
| `visible` | In frame, facing camera, unoccluded, legible | Describe the part that supports the thesis |
| `partial` | In frame but cropped, occluded, foreshortened, blurred, or low-contrast | Describe the visible portion and the occlusion; do not complete it |
| `hidden` | Outside the visible surface set, behind an occluder, internal, or on the far side | Omit. Use a cue only if supported. Negative if the model would invent it |
| `off_frame` | Exists in the world but outside the crop | Omit. Negative if it is likely to intrude |

Do not use `hidden` for something that is merely unimportant. A small visible scratch is still visible; it may simply not deserve prompt space.

## Legibility

Separate existence from readability:

- **Geometrically visible, not readable.** A serial number at three meters, a face behind frosted glass, a dark engraving in shadow.
- **Readable.** High contrast, sufficient size, correct focus, facing the camera.

For unreadable features, prompt the visual effect (a faint line of engraving, a blurred glyph band) rather than specific content. Never invent the content of unreadable text. If the text matters, change the view or ask for it.

## Partial Visibility Cases

- **Frame crop.** The subject extends beyond the frame edge. Describe the cropped part as absent from frame, not as missing from the world.
- **Foreground occlusion.** A nearer object blocks part of the subject. Describe the occluder and the visible remainder.
- **Self-occlusion.** The object blocks itself: a mouth interior, the far side of a handle, the inside of a bowl.
- **Atmospheric occlusion.** Fog, smoke, dust, or water reduces contrast and hides distance. This can be partial or complete.
- **Depth of field.** A feature can be in frame but out of focus. It reads as shape and color, not detail.
- **Motion blur.** A moving part reads as a streak; detail is unavailable.
- **Reflection or transparency.** A feature may be visible only as a reflection, silhouette through glass, or shadow. Treat it as a cue, not as a direct view.
- **Lighting occlusion.** A feature may be in deep shadow. It is present but not legible.

## Hidden Cues

A hidden feature may still leave evidence. Use only cues that the geometry, material, and light support.

| Cue | Prompt language | Constraint |
| --- | --- | --- |
| Silhouette | "a low bulge breaks the outline on the left" | The hidden mass must actually intersect the silhouette |
| Protrusion | "a short key shaft protrudes past the rear edge" | The part must extend beyond the occluder |
| Cast shadow | "a thin shadow falls across the table behind it" | Light direction must make the shadow land in frame |
| Reflection | "a distorted second ring appears in the polished base" | The reflective surface and angle must be plausible |
| Transparency | "a blurred inner ring shows through the smoked glass" | The occluder must be transparent or translucent |
| Contact shadow | "the base sits in a tight dark contact shadow" | The object must rest on the surface |
| Environmental response | "heat shimmer above the vent" | The hidden process must produce a visible effect |

Do not use a cue as an excuse to describe the hidden part. "A key-shaped shadow" is still a description of the key if the dump did not establish it. Prefer the visible effect without naming the cause when the cause is meant to be unknown.

## Prompt Actions

Map every tracked feature to one action:

- `describe`: visible and important. Use concrete visual language.
- `suggest`: partial, illegible, or hidden-with-cue. Use only the visible evidence.
- `omit`: irrelevant or invisible. Keep it out of the positive prompt.
- `negative`: likely to be invented by the model. Put it in the negative prompt.

A feature can be important to the story and still be `omit`. The image is not a wiki page.

## Framing And Lens

- **Aspect ratio** determines what fits. A tall object in a wide frame needs distance or crop.
- **Shot scale** determines detail. A full-body shot cannot also show a fingerprint.
- **Occupancy** determines hierarchy. Give the primary subject the largest readable area, unless the brief is about scale or environment.
- **Foreground occlusion** creates depth but can hide the subject. Use it deliberately.
- **Camera height** sets the horizon and the viewer's relationship to the subject. Low camera makes the subject dominate; high camera makes it observed or small.
- **Wide lens** expands space and exaggerates near objects. **Telephoto** compresses depth and isolates. Do not combine both in one prompt.
- **Depth of field** chooses the reading order. If everything is sharp, the viewer must find the subject; if the subject is sharp and the background soft, the hierarchy is explicit.
- **Crop** is a compositional decision. A cropped head is not a head that does not exist; do not describe it as absent from the world.

## Consistency Checks

- Shadows point away from the key light and agree in softness.
- Reflections show the environment that actually exists at that angle.
- The horizon height agrees with camera height and pitch.
- The scale anchor is plausible at the stated distance.
- Lens compression agrees with the distances in the layout.
- Occluders are between the camera and the hidden feature, not beside it.
- Transparent surfaces reveal what is actually behind them, with plausible distortion.
- A feature described as visible is inside the frame at the chosen crop.

## Multi-View

One world model can produce several views. Each view needs its own state file, visibility ledger, and prompt. Keep the world fixed and change only the camera.

- Repeat invariants: dimensions, materials, colors, damage, light direction, time of day.
- Do not show a feature in one view that the other view proves is absent.
- Do not average two views into one prompt.
- If a new dump changes the world, update every view that depends on it, not just the current one.
- Name views consistently: `front`, `front-left-three-quarter`, `rear-right`, `top-down`, `detail-dome`.

## Choosing A View

1. Honor the user's stated view or implied viewpoint ("seen from the doorway", "as the keeper looks up").
2. If no view is given, choose the one that shows the defining silhouette, the primary material, and one scale anchor.
3. Protect intentional unknowns: if the dump withholds the face or the interior, choose a view that does not accidentally reveal it.
4. Prefer a readable view over a dramatic one. Drama that hides the subject is a failed product image and a weak character image.
5. State the camera in the reconstruction summary so the user can ask for a different one.

## Visibility Ledger

For each feature:

| Field | Answer |
| --- | --- |
| Entity / feature | What is being tested |
| Surface zone | front, back, left, right, top, bottom, internal |
| Frustum | inside, cropped, outside |
| Facing | frontal, angled, grazing, away |
| Occluder | none, or what blocks it |
| Legibility | readable, partial, illegible |
| State | visible, partial, hidden, off_frame |
| Cue | direct, silhouette, shadow, reflection, transparency, protrusion, none |
| Prompt action | describe, suggest, omit, negative |

If the ledger is empty, the prompt is guessing.
