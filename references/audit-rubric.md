# Prompt Audit Rubric

Read this when checking a finished prompt, a reconstruction, or an update before delivery.

## Two Audits

Audit in this order:

1. **Reconstruction audit.** Is the state internally consistent and does it match the dump?
2. **Prompt audit.** Does the prompt render exactly the visible reconstruction for one camera?

A well-written prompt derived from a bad reconstruction is still wrong.

## Reconstruction Audit

Score each item 0 or 1:

| Check | Question |
| --- | --- |
| Subject identity | Is the subject or scene recognizable from the state? |
| Geometry | Are form, proportion, and component hierarchy coherent? |
| Scale | Is there a measurement, ratio, or anchor that proves size? |
| Contact | Does everything rest on, hang from, or connect to something plausible? |
| Materials | Are surface, finish, and condition specified rather than named? |
| Camera | Is there one camera station with height, distance, angle, and lens? |
| Visibility | Does every tracked feature have a state and prompt action? |
| Occlusion | Are hidden surfaces explained by facing, occlusion, or crop? |
| Light | Do key, fill, shadows, and reflections agree? |
| Conflicts | Are contradictions resolved or explicitly accepted? |
| Origins | Are inferences and defaults marked? |
| Compactness | Is the state free of non-visual lore and duplicate facts? |

9-12: usable. 6-8: revise before prompting. 0-5: rebuild.

## Prompt Audit

Score each item 0 or 1:

| Check | Question |
| --- | --- |
| Visual thesis | Does one priority dominate? |
| Camera | Are height, angle, lens, shot scale, framing, and focus controlled? |
| Composition | Is frame placement and occupancy explicit? |
| Scale | Is scale proven visibly? |
| Subject | Is the visible form described, not just named? |
| Material | Are surface and finish visible in the prompt? |
| Environment | Is the world defined, including important absences? |
| Lighting | Is light direction and quality plausible and consistent? |
| Color and finish | Are palette, saturation, contrast, and medium controlled? |
| Hidden detail | Are hidden and off-frame features absent from the positive prompt? |
| Negatives | Are likely failures prevented without contradictions? |
| Platform | Is the formatting correct for the target model? |

9-12: ready. 6-8: revise. 0-5: rebuild from the state.

## Update Audit

When the user adds information, also check:

| Check | Question |
| --- | --- |
| Rebuild | Was the prompt rebuilt from the updated state, or merely appended to? |
| Propagation | Did changed dimensions or materials update every dependent feature? |
| Visibility | Was the visibility ledger recomputed for the current camera? |
| Staleness | Are superseded facts gone from the positive and negative prompts? |
| Delta | Does the reported change match the actual prompt change? |
| Version | Is the prompt version or update note present? |

An update that leaves an old material, old dimension, or old hidden feature in the prompt has failed even if the new sentence is correct.

## Script Checks

Validate the state:

```bash
python scripts/scene_state.py validate image-scenes/<slug>/scene-state.json
```

Check the prompt for hidden-feature leaks and missing camera or lighting controls:

```bash
python scripts/scene_state.py check --state image-scenes/<slug>/scene-state.json --file image-scenes/<slug>/prompt.md --platform portable
```

Run the sibling prompt linter when `directing-image-prompts` is available:

```bash
python ../directing-image-prompts/scripts/prompt_lint.py --text "<prompt>" --platform portable
```

The scripts check mechanical completeness and contradictions. They do not judge taste, originality, or whether a real image will be beautiful.

## Red Flags

- The prompt lists rear, internal, or off-frame detail that the camera cannot see.
- The prompt summarizes lore instead of describing visible evidence.
- A front view describes a back surface, or a high view describes an underside.
- A "giant" subject has no scale anchor and a level camera.
- Light comes from one direction and shadows fall toward it.
- The hidden back of the object is described because it is interesting, not because it is visible.
- A new dump was pasted onto the old prompt, leaving the old material or old camera.
- A conflict was silently averaged into an impossible object.
- "No text" appears next to a quoted inscription.
- The negative prompt negates visible elements.
- The prompt uses state vocabulary: entity, visibility, prompt_action, ledger.
- Every detail has equal emphasis, so nothing dominates.
- The reconstruction has no camera, so "visible" is undefined.

## Revision Order

1. Fix the reconstruction, not the prompt, if the error is structural.
2. Remove contradictions and stale facts.
3. Fix the camera and the visibility ledger.
4. Restore the visual thesis.
5. Add missing visual controls.
6. Tighten the negative prompt.
7. Format for the platform.
8. Cut detail that does not earn its place.

## Cross-View Audit

For multiple views of one world:

- Dimensions, materials, damage, and time of day match across views.
- A feature hidden in one view is not invented in another unless the world model supports it.
- Each prompt states its own camera and does not rely on "same as before."
- The lighting direction is consistent with the time of day, even when the camera changes.
- The same visual thesis is recognizable, unless a different mood was requested.
