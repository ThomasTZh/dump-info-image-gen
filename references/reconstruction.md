# Reconstruction

Read this when building or revising the object or scene model. The reconstruction is the intermediate artifact between the dump and the prompt.

## Principle

A reconstruction is a spatial hypothesis, not a synopsis. It must answer:

- What exists, and what is it made of?
- Where is it, how big is it, and what does it rest on or connect to?
- Which surfaces face the camera, and which are turned away?
- What blocks the line of sight to each feature?
- Where does light come from, and what does it reveal?

If the reconstruction cannot answer these, the prompt will guess. Guessing is acceptable only when marked as `default` or `inferred`.

## Object Reconstruction

Build the object in this order:

1. **Identity and category.** What kind of thing is it? The category sets plausible proportions, materials, and construction logic. Do not let category convention override stated facts.
2. **Silhouette and proportion.** Overall envelope, dominant axis, symmetry, taper, mass distribution. This is what the viewer reads first.
3. **Component hierarchy.** Whole object, major assemblies, sub-parts, surface details. Example: instrument = base, frame, glass dome, concentric rings, dial face, handle, rear winding mechanism.
4. **Dimensions and scale.** Height, width, depth, diameters, thicknesses, clearances. Use ranges when the dump is approximate.
5. **Materials and finish.** Base material, coating, color, roughness, specular behavior, translucency, seams, wear, damage, repairs.
6. **Articulation and pose.** What is fixed, what is rotated, opened, folded, or under load? Pose changes silhouette and occlusion.
7. **Placement and contact.** What supports it? Where does it touch the ground, table, wall, or another object? Contact shadows anchor it.
8. **Surface zones.** Assign features to front, back, left, right, top, bottom, or internal. A feature with no assigned surface cannot be tested for visibility.
9. **Structural integrity.** Are the parts physically connected? Does the handle attach to the frame? Does the glass dome seal the rings? Impossible joins read as generated artifacts.

A useful object state has one primary entity and only the secondary entities that affect the image. Do not model every screw.

## Scene Reconstruction

A scene needs a simple map before it needs adjectives.

1. **Coordinate frame and ground.** Define the ground plane, eye height, and a rough left-right/front-back axis. State the unit.
2. **Layout.** Place each significant entity with a position, orientation, and distance from the camera. Use relative descriptions when exact coordinates are absent: "eight meters beyond the doorway, slightly left of the axis."
3. **Depth layers.** Foreground, midground, background. Decide which layer carries the subject and which carries context.
4. **Occluders.** Walls, columns, furniture, terrain, crowd, vehicles, smoke. An occluder is part of the visibility model, not decoration.
5. **Boundaries.** Where does the world end in frame? Horizon, wall, ceiling, fog bank, frame edge. This controls enclosure and escape.
6. **Apertures and light sources.** Windows, doors, skylights, lamps, fire, sky. Every source needs a direction and a quality.
7. **Atmosphere.** Air clarity, haze, dust, rain, smoke, spray. Atmosphere changes contrast and depth; it also hides detail.
8. **Scale cues.** Doors, people, furniture, vehicles, handrails, known objects. A scene without scale cues reads as a miniature or a diagram.
9. **Off-frame world.** Only model what affects the image: light spilling from a corridor, a shadow entering frame, a reflection of something outside the crop.

A scene state can have several entities: primary subject, supporting subjects, environment volumes, and props. Role labels keep the prompt from giving equal weight to all of them.

## Geometry Discipline

- **Preserve units.** If the dump says meters, do not silently switch to feet. If it gives a range, keep the range.
- **Mark approximations.** `~0.8 m` is honest. `0.8 m` implies measurement. Do not add precision the dump does not support.
- **Prefer ratios when measurements are absent.** "The dome is about one-third of the total height" is renderable. "Large dome" is not.
- **Respect support and gravity.** A heavy object needs a base, a mount, a table, or a suspension. Floating is a deliberate exception, not an accident.
- **Check symmetry.** If the object is symmetrical, a feature on one side implies the matching feature on the other unless the dump says otherwise. If it is asymmetrical, say which side.
- **Check clearances.** Handles need room; doors need swing space; rings need gaps; a figure needs headroom.
- **Do not over-model the hidden side.** The back can be less detailed, but it cannot be geometrically impossible. Hidden parts still affect silhouette, weight, and edge behavior.

When dimensions conflict, choose a coherent set and propagate it. A height change can change camera distance, frame occupancy, contact shadow size, and the apparent scale of every nearby object.

## Materials And Surfaces

For each material, record only what changes the image:

- **Base color** separate from reflected or transmitted color.
- **Roughness / finish**: matte, satin, polished, wet, dusty, oily.
- **Specular behavior**: broad soft highlights, sharp highlights, anisotropic streaks.
- **Transparency / translucency**: clear glass, smoked glass, frosted, amber resin, thin fabric.
- **Pattern**: grain, weave, striation, engraving, inlay, cracks.
- **Seams and construction**: rivets, welds, dovetails, molded edges.
- **Wear and repair**: chipped edges, patina, scorch, replacement panels, mismatched fasteners.
- **Condition**: new, maintained, neglected, damaged, partially destroyed.

Distinguish material from lighting. A dark object is not necessarily black; a warm object is not necessarily brass. If the dump only gives color, mark the material as inferred.

Thin, translucent, or reflective hidden parts can still affect the image: a hidden light source may glow through a seam; a hidden mechanism may cast a shadow; a hidden frame may show through frosted glass. Treat these as cues, not as visible detail.

## Environment And Light

Derive light from the environment before choosing a mood:

- Time of day and weather set the key direction and color.
- Practical sources (lamp, fire, screen, molten metal) set local color and falloff.
- Apertures (window, doorway, cave mouth) set the direction and softness.
- Bounce surfaces (sand, snow, water, warm walls) set fill color.
- Atmosphere scatters light and lowers contrast with distance.

Then make light camera-relative: "key from frame upper left" is usable; "lit from the east" may not be. Shadows must point away from the key, reflections must show the environment that exists, and rim light must come from a plausible source behind the subject.

## Scale

Scale is a claim about the world, not an adjective.

- Use a stated measurement when available.
- Otherwise use a familiar anchor: human adult, doorway, chair, vehicle, hand, brick, known object.
- Otherwise use a frame ratio: "the subject fills four-fifths of the frame height."
- For colossal subjects, distance and atmosphere prove scale better than the word "giant."
- For tiny subjects, a macro lens plus a known surface grain or fiber proves scale.
- Scale anchors must be plausible at the chosen distance. A human standing ten meters from a camera will be small; do not use a figure that is too small to read as a scale cue.

## Origin And Confidence

Every non-trivial fact should carry an origin:

- **stated**: directly in the dump.
- **inferred**: a logical consequence, a design deduction, or a physical necessity.
- **default**: a choice made to complete the image.

An inference is allowed to shape the image, but the prompt should render its visible consequence, not assert its cause. "Ancient" is a cause. "Edges rounded and polished by handling" is a visible consequence. "Dwarven make" is a cause. "Tight, load-bearing joinery with oversized corner brackets" is a consequence, and only if the dump supports that design language.

When an inference is uncertain, prefer a neutral visual that can survive being wrong: generic wear instead of a specific culture's ornament, standard glass instead of a named optical effect.

## Internal Consistency Checks

Before visibility:

- **Contact**: does every object touch its support plausibly?
- **Support**: is the mass carried by something that can carry it?
- **Occlusion**: does the layout actually allow the claimed sightline?
- **Material logic**: does a thin glass dome support a heavy ring? Does a rusty hinge still open?
- **Scale**: do the anchors and the object agree?
- **Light**: do all shadows and highlights agree on one dominant direction?
- **Frame**: does the subject fit at the chosen lens and distance?
- **Symmetry**: are paired features consistent?
- **Function**: does the form support the stated use without becoming a diagram?

## Update Semantics

Update the state as keyed records, not as prose.

- **New feature**: add it to an entity and assign a surface. Compute visibility before adding it to the prompt.
- **Changed dimension**: update the entity, then recompute contact, placement, frame occupancy, occlusion, and any dependent scale anchor.
- **Changed material**: update color, finish, reflections, and negative constraints together. Do not keep "brass" in the prompt after the material becomes copper.
- **Moved feature**: change its surface, then recompute visibility. A feature moved to the rear may disappear from the current view entirely.
- **Removed feature**: delete it from the entity and from visibility; remove its positive description and its negative constraint if it was only there to suppress it.
- **Changed identity**: if the object or scene becomes a different thing, rebuild the state rather than patching. Say that you rebuilt.
- **Changed time or weather**: update light, atmosphere, reflections, and shadow softness, then reassess legibility.
- **Changed camera**: keep the world fixed and recompute only visibility, framing, focus, and the prompt.

Keep a short prompt version note so an update can be compared with its predecessor.

## Reconstruction Brief

The state is machine-readable. The brief is the human/model-readable projection used to write the prompt. Generate it with:

```bash
python scripts/scene_state.py brief image-scenes/<slug>/scene-state.json
```

The brief should expose the thesis, camera, scale, entities, features, visibility ledger, environment, light, color, assumptions, and conflicts. If a detail is not in the brief, the prompt should not depend on it.
