---
name: dump-info-image-gen
description: Use when the user dumps large, messy, or incremental information about an object or scene (specs, lore, notes, measurements, reference details, worldbuilding) and wants an image-generation prompt, a visual reconstruction with a viewing angle and visible-versus-hidden surfaces, multi-view prompts, or a rebuilt prompt after each new dump. Not for polishing an existing prompt that has no source dump.
---

# Dump Info Image Gen

## Overview

Turn an information dump into a persistent visual reconstruction, then derive image prompts from that reconstruction.

The dump is evidence, not prompt text. Separate what is directly visible, what shapes geometry and occlusion, and what is merely lore. The prompt renders only what the chosen camera can see. Hidden information can influence silhouette, edge protrusion, shadow, or framing, but it must not be described as seen. Rebuild the reconstruction after every new dump instead of appending new facts to the old prompt.

## Modes

- **Build**: first dump, no existing state.
- **Update**: new dump, correction, contradiction, or retraction.
- **View**: same world model, different camera.
- **Render**: state exists, rewrite the prompt only.
- **Audit**: check a prompt against its state.

## Workflow

1. **Intake.** Read the dump in passes: subject and scene nouns first, then geometry and spatial claims, then materials and surfaces, then everything else. Split it into claims and classify each as visual, structural, implied cue, non-visual, conflict, or gap. Record whether each claim is stated, inferred, or defaulted. Do not echo the whole dump back. See `references/intake-and-triage.md`.

2. **Reconstruct.** Create or update the world model: entities, component hierarchy, dimensions, materials, placement, pose, scale, environment, and light. New explicit information supersedes old information. When a dimension or placement changes, propagate it to contact points, occlusion, and scale before touching the prompt. Mark every inferred detail. See `references/reconstruction.md`.

3. **Choose the view.** Define a camera station: height, distance, azimuth, elevation, lens or field of view, shot scale, framing, focus, and aspect ratio. Prefer a view that shows the defining features and keeps intentionally unknown parts unknown. Use the user's stated viewpoint when one exists. One view produces one prompt. See `references/camera-and-visibility.md`.

4. **Compute visibility.** For every tracked feature decide visible, partial, hidden, or off-frame. Use frustum bounds, surface facing, occlusion, and legibility. Distinguish geometrically visible from readable: a black surface in shadow may be in frame but not legible. Build the visibility ledger, including cues such as silhouette, protrusion, shadow, or reflection for hidden parts. See `references/camera-and-visibility.md`.

5. **Synthesize.** Write the prompt from the visible set only. Lead with one visual priority, then use the normal visual stack: medium, camera, composition, subject, environment, light, color, and constraints. Convert state fields into image language; never paste state JSON or claim IDs into the prompt. Use `references/prompt-synthesis.md` and `references/platform-profiles.md`.

6. **Validate and persist.** Validate the state, run the prompt consistency check, and run the sibling prompt linter if `directing-image-prompts` is installed. Save the state and prompt. On an update, report what materially changed. See `references/audit-rubric.md`.

## State

The state is the source of truth; the prompt is a derived artifact.

- Default location: `image-scenes/<slug>/scene-state.json` and `image-scenes/<slug>/prompt.md` in the user's workspace.
- Multiple views of one world: same slug, one state file per view, named `scene-state.<view-id>.json`.
- If the user does not want files, keep a compact `State:` block in the answer and update it in place. Do not rely on conversational memory alone for a long-running reconstruction.
- The canonical schema and update rules are in `references/scene-state.md`.
- `scripts/scene_state.py` can initialize, validate, render a reconstruction brief, diff two states, and check a prompt for hidden-feature leaks.

## Rules

- **Render the view, not the encyclopedia.** A fact that cannot affect the chosen image belongs in the state, not the prompt.
- **Never describe a hidden surface as visible.** Put it in the negative prompt only when the model is likely to invent it.
- **Rebuild, do not append.** Every new dump triggers a fresh selection from the updated reconstruction, even if most of the prompt survives.
- **A new dump is the trigger.** Reconstruct and rewrite without waiting for a separate "update the prompt" request.
- **No visible consequence, no forced visual change.** If new information is pure lore, record it as ignored or structural and say the image is unchanged. Do not invent a visual change to justify the update.
- **State facts, not interpretations.** Prefer visible evidence ("edges rounded and polished by handling") over its cause ("ancient") unless the cause is itself visible.
- **Do not invent readable text, logos, measurements, or identities.** If exact text is required but absent, ask once; otherwise reserve clean space and exclude text.
- **Non-visual facts do not render.** Backstory, smell, sound, mechanics, and relationships matter only through a concrete visible consequence, and that consequence is an inference.
- **One visual priority.** Ten interesting details do not fit one image. Rank them by what the viewer must immediately understand.
- **Keep light, shadow, reflection, and scale mutually consistent.** Camera height sets the horizon; light direction sets shadow direction; lens sets compression.
- **Ask only blocking questions.** A missing camera is a creative choice. Missing subject identity, contradictory geometry, or required exact text can block.

## Update Protocol

When new information arrives:

1. Diff the new claims against the current state.
2. Apply supersessions, corrections, and retractions; log unresolved conflicts.
3. Recompute geometry-dependent placement, contact, and occlusion.
4. Recompute visibility for the current camera. If the new information makes a better view necessary, change the view and say why.
5. Rewrite the prompt from scratch from the updated visible set.
6. Report added, changed, removed, newly visible, newly hidden, ignored, and still uncertain.

Do not preserve old prompt sentences merely because they were already written.

## Output Shape

Default response:

```text
Reconstruction:
- Thesis: ...
- View: ...
- Visible: ...
- Hidden / off-frame: ...
- Assumptions: ...

Prompt:
...

Changes: ...            (updates only)
Open: ...               (blocking questions only)
```

If the user asks for the prompt only, still update the state, then return the prompt without the commentary.

## Resource Map

| Need | Load |
| --- | --- |
| Read a noisy or oversized dump, resolve conflicts | `references/intake-and-triage.md` |
| Build the object or scene model | `references/reconstruction.md` |
| Choose a camera and compute visible versus hidden surfaces | `references/camera-and-visibility.md` |
| State schema, enums, file layout, update semantics | `references/scene-state.md` |
| Turn reconstruction into prompt language | `references/prompt-synthesis.md` |
| Platform-specific formatting | `references/platform-profiles.md` |
| Audit a prompt against the reconstruction | `references/audit-rubric.md` |
| Worked dump, update, and prompt revisions | `references/examples.md` |
| Startable state and report files | `assets/templates/*.json`, `assets/templates/*.md` |

## Scripts

Initialize a state:

```bash
python scripts/scene_state.py init --out image-scenes/<slug>/scene-state.json --slug <slug> --mode object
```

Validate, render a brief, and compare states:

```bash
python scripts/scene_state.py validate image-scenes/<slug>/scene-state.json
python scripts/scene_state.py brief image-scenes/<slug>/scene-state.json
python scripts/scene_state.py diff old-state.json new-state.json
```

Check a finished prompt for hidden-feature leaks and missing visual controls:

```bash
python scripts/scene_state.py check --state image-scenes/<slug>/scene-state.json --file image-scenes/<slug>/prompt.md --platform portable
```

The checker is a guardrail against rendering impossible or hidden detail; it is not a taste judge. For broader prompt completeness, also run `directing-image-prompts/scripts/prompt_lint.py` when that skill is available.

## Platform Output Rule

- **Portable / unknown**: natural-language prompt plus `Negative:` when useful.
- **Midjourney**: compact one-line prompt, concise `--no` terms, aspect ratio when useful.
- **Stable Diffusion, SDXL, Flux**: `Positive:` and `Negative:` blocks.
- **DALL-E / OpenAI image models**: natural-language instructions with exact placement, quoted text, and edit invariants.

## Quality Gate

Before delivering:

- The reconstruction has a camera station and a visibility ledger.
- Every described feature is visible or partial at that camera; every hidden feature is absent from the visible prompt.
- Hidden cues are plausible for the light and material.
- Scale is proven by an anchor, ratio, or known object.
- Light direction, shadows, reflections, and environment agree.
- One visual priority dominates and lore did not become decoration.
- The prompt is platform-formatted and does not leak state terminology.
- Negative constraints target likely failures without contradicting the positive prompt.
- On updates, the prompt was rebuilt and the delta is reported.

## Common Failure Pattern

Weak behavior: the dump becomes a long prompt that lists every fact, including the rear mechanism, internal wiring, guild history, and sealed compartments that the camera cannot see.

Strong behavior: the reconstruction keeps those facts in the state, marks the rear and interior hidden, uses the hidden mass only for the silhouette, and the prompt describes the visible front three-quarter surfaces, the light, the scale anchor, and the absence of text and rear detail.

For complete worked revisions, load `references/examples.md`.
