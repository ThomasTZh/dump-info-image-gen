# Intake And Triage

Read this when the dump is long, repetitive, contradictory, or mixes visual description with lore, mechanics, and backstory.

## Goal

Convert raw text into a compact set of claims that can drive a reconstruction. The dump is evidence. The prompt is not a summary of the dump.

## Read In Passes

Do not try to hold every sentence at once. Read in this order and keep a running ledger:

1. **Orientation.** What is the subject or scene? Is this an object portrait, a location, a character, a product, or a moment? Does the user name a viewpoint, platform, aspect ratio, or output purpose?
2. **Visual extraction.** Shapes, proportions, colors, materials, surface condition, visible parts, pose, placement, environment, light.
3. **Structural extraction.** Component hierarchy, hidden surfaces, interiors, dimensions, distances, occluders, mechanisms, room counts, scale relationships.
4. **Non-visual extraction.** History, purpose, ownership, sound, smell, behavior, relationships, rules, factions, chronology.
5. **Conflict and gap pass.** What is stated twice with different values? What is missing but necessary for this image?

Skip decorative repetition. If the dump says "very very old" six times, that is one claim, not six.

For very long dumps, process in chunks. Extract conclusions into the ledger after each chunk instead of re-reading the raw text. Treat later chunks as new evidence that can revise earlier conclusions; do not let the first chunk lock the reconstruction.

## Claim Ledger

Use a compact working table. It does not need to be saved unless the user wants an audit trail.

| ID | Claim | Class | Origin | Scope | Confidence | Action |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | 0.8 m tall | V | stated | whole object | high | use |
| C2 | rear winding key | S | stated | back | high | hidden at current view |
| C3 | smells of ozone | N | stated | atmosphere | high | ignore for image |
| C4 | "ancient" | I | stated | condition | medium | render wear only if visible |
| C5 | brass / copper | X | stated twice | materials | low | resolve before prompt |

Class and origin are the important fields. Confidence is a judgement, not a measurement.

## Classes

**V: visual.** Directly changes pixels at the chosen view. Shape, silhouette, color, material, finish, visible damage, pose, visible light, visible environment, readable text.

**S: structural.** Shapes geometry, proportion, contact, occlusion, or silhouette, but is not necessarily described. Internal mechanism, rear vents, number of floors, wall thickness, distance between buildings, what is inside a sealed case. Structural facts matter even when invisible because they constrain what can be seen.

**I: implied cue.** A non-visual fact that plausibly produces a visible consequence. "Built for deep-sea pressure" may imply thick ribs and small windows, but only if the dump or the design logic supports it. Mark the consequence as inferred. Never turn a mood or a backstory into a concrete object without a reason.

**N: non-visual.** Backstory, motivation, smell, sound, taste, relationships, ownership, rules, mechanics with no visible outcome, praise, rankings, repeated adjectives. Keep out of the prompt. A short `ignored` note in the state prevents re-litigating it later.

**X: conflict.** Two claims cannot both be true, or the same fact has incompatible values. Resolve explicitly.

**R: requirement.** Explicit constraints: exact text, must-include elements, must-avoid elements, aspect ratio, platform syntax, reference-image invariants.

**G: gap.** Something the image needs that the dump does not supply. Most gaps are filled with a marked default; only blocking gaps become questions.

## Relevance Tests

Run these before promoting a claim into the prompt:

- **Pixel test.** At this camera, would the claim change at least one pixel? If no, it is not visual.
- **Geometry test.** Would it change a proportion, contact point, silhouette, or occlusion? If yes, keep it structural even when hidden.
- **Legibility test.** Would it change what the viewer can identify, not merely what exists? A tiny background label may exist but be unreadable.
- **Absence test.** Does the dump explicitly deny something ("no windows", "never shows its face")? Record it as a constraint or absence rule; do not silently drop it.
- **Story test.** Does it only explain why something looks the way it does? If the visible cause is absent, it is non-visual.

## Common Traps

- **Negation.** "No rivets" is a constraint. "Seamless" is the positive form. Do not write "no rivets" into a positive description if "smooth, unbroken surface" is clearer.
- **Hedging.** "Possibly", "rumored", "some say", "in-universe legend" lowers confidence. Do not harden a rumor into visible fact.
- **In-world testimony.** A character saying "it is indestructible" is not a visual specification. Treat it as low-confidence unless corroborated by description.
- **Simile and metaphor.** "Like a cathedral" gives scale and proportion, not stone arches. Extract the mechanism: verticality, vaulting, dimness.
- **Function.** "A weapon" does not define a shape. Derive form from stated structure, not from genre convention.
- **Capability.** "Invisible", "shapeshifting", "holographic" cannot be rendered literally. Decide what the camera actually records: refraction, distortion, a visible projection, an empty silhouette.
- **Numbers.** Preserve units and ranges. Do not convert a rough "about three stories" into "10.2 m" unless you mark the conversion as inferred.
- **Names.** A name is not visible text. Do not render a title, guild name, or logo unless the dump says it is written and readable at this view.
- **Relationships.** "Twin of X" matters only if the visible resemblance matters. Otherwise it is non-visual.
- **Chronology.** "Rebuilt after the fire" is non-visual unless charring, mismatched replacement parts, or scorch marks are stated or directly implied.
- **Lists without attachment.** A list of features may not say which surface each is on. Assign surfaces explicitly and mark the assignment as inferred or default.
- **Repeated emphasis.** "Massive, huge, colossal" is one scale claim. Prefer a measurement, ratio, or anchor.

## Conflict Policy

Resolve in this order:

1. Explicit user correction or retraction in the latest message.
2. Latest explicit statement, when the fact is mutable (condition, time of day, current damage).
3. Specific or measured statement over general impression.
4. Direct description over in-world hearsay, legend, or a character's claim.
5. If still incompatible, choose the version that best supports the requested image and record the conflict as `accepted` or `open`.

Never merge incompatible geometry into one object. A three-story tower and a five-story tower cannot both be true; pick one for the render and state the choice. Color conflicts are less destructive than structural conflicts, but still log them.

Mutable facts (weather, time, damage, occupants) follow the latest statement. Immutable facts (material, origin, dimensions) need a correction or a specific override to change.

## Retractions And Supersessions

- "Ignore the rear key" removes the feature or marks it absent. Remove it from the visible set and from any positive prompt.
- "Actually, it is copper" replaces the material everywhere it propagates: color, reflections, patina, weight cues, and negative constraints about brass.
- "The plate is on the rear-left, not the left" moves the feature, then recomputes visibility.
- Unmarked contradictions require a choice and a log entry. Do not silently average values.

## Gaps

Most gaps are creative space. Fill them with the most conservative visual default that does not contradict the dump, and mark it `default`.

Ask a question only when the gap blocks a usable image:

- The subject or scene cannot be identified.
- Two incompatible geometries have no clear winner, and the choice changes the composition.
- Exact readable text is required but not supplied.
- The user requests a specific view that the geometry makes impossible.
- A required reference image is missing.

Do not ask for camera height, lens, palette, background, or minor pose details. Choose them, state them, and move on.

Ask at most one compact question. If the user is likely to prefer progress over precision, proceed and expose the assumption in the reconstruction summary.

## Images In The Dump

When the dump includes images, assign each a role before using it:

- **Reference image**: borrow only the named aspect (style, identity, palette, material).
- **Supporting image**: use only for the named prop, texture, pose, or background.
- **Edit target**: preserve composition, identity, lighting, and perspective unless the user asks to change them.

Record the role and the invariants in the state. Do not let an image silently override a stated text fact.

## Output

Keep the working ledger compact. Persist only resolved facts, assumptions, conflicts, and ignored material in the state. Do not quote the dump back to the user, and do not list every ignored line; summarize the material ones.
