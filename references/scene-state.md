# Scene State

Read this when creating, editing, validating, or comparing the reconstruction state. The state is the canonical reconstruction. The prompt is derived from it.

## File Layout

Single view:

```text
image-scenes/<slug>/
  scene-state.json
  prompt.md
  reconstruction.md      (optional generated brief)
```

Multiple views of one world:

```text
image-scenes/<slug>/
  scene-state.front.json
  scene-state.front-left-three-quarter.json
  scene-state.rear-right.json
  prompt.front.md
  prompt.front-left-three-quarter.md
  prompt.rear-right.md
```

`world_id` groups views. `slug` names the project. `camera.view_id` names the view. Reuse the same entities, materials, and dimensions across views; change only the camera and the visibility ledger.

If the user does not want files, keep the same fields in a compact inline `State:` block. The structure still applies.

## Top-Level Fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | int | yes | `1` for this schema |
| `world_id` | string | no | Shared identifier for multi-view worlds |
| `slug` | string | yes | Project identifier, lowercase hyphens |
| `updated` | string | yes | ISO date `YYYY-MM-DD` |
| `mode` | string | yes | `object` or `scene` |
| `platform` | string | yes | Target image model or `portable` |
| `visual_thesis` | string | yes | One sentence the viewer must understand |
| `scale_anchors` | array | no | Known objects and sizes used to prove scale |
| `entities` | array | yes | At least one subject or environment entity |
| `environment` | object | yes | Location, time, weather, atmosphere, absences |
| `camera` | object | yes | One camera station for this state |
| `visibility` | array | yes | Feature visibility ledger for this camera |
| `lighting` | object | yes | Key, fill, rim, time, color temperature, shadows |
| `color_finish` | object | yes | Palette, saturation, contrast, medium, grain |
| `style` | string | yes | Medium and visual style |
| `constraints` | object | yes | Must include, must avoid, exact text |
| `assumptions` | array | no | Inferred or defaulted decisions |
| `conflicts` | array | no | Resolved, accepted, or open contradictions |
| `ignored` | array | no | Non-visual dump material and why it is ignored |

## Entity Fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | Stable identifier, unique in the state |
| `name` | string | yes | Short display name |
| `role` | string | yes | `primary`, `secondary`, `environment`, or `prop` |
| `origin` | string | yes | `stated`, `inferred`, or `default` |
| `geometry` | string | yes | Form, proportion, orientation, hierarchy |
| `dimensions` | string | no | Measurements or ranges; mark estimates with `~` |
| `materials` | array | no | Base materials |
| `colors` | array | no | Dominant visible colors |
| `finish` | string | no | Surface finish, texture, wear |
| `condition` | string | no | New, maintained, damaged, decayed |
| `placement` | string | no | Position in the world and frame |
| `pose` | string | no | Orientation, action, articulated state |
| `features` | array | yes | Tracked features, may be empty for an environment |

Keep only entities that affect the image or its consistency. An environment entity can represent a room, terrain volume, sky, or crowd mass without modeling every prop.

## Feature Fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | Stable identifier, unique within the entity |
| `name` | string | yes | Short feature name used in the visibility ledger |
| `surface` | string | yes | `front`, `back`, `left`, `right`, `top`, `bottom`, `internal`, or a combined zone |
| `description` | string | yes | What it looks like on the surface |
| `origin` | string | yes | `stated`, `inferred`, or `default` |

Feature names should be concrete and distinctive, because the prompt checker uses them to detect hidden-feature leaks. Avoid names like "detail" or "part".

## Camera Fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `view_id` | string | yes | Short view name |
| `height` | string | yes | Camera height above ground |
| `distance` | string | yes | Camera to subject distance |
| `azimuth_deg` | number | yes | Horizontal angle from the subject's front |
| `elevation_deg` | number | yes | Vertical angle above the horizon |
| `lens` | string | yes | Focal length equivalent or field of view |
| `shot_scale` | string | yes | How much of the subject is in frame |
| `framing` | string | yes | Placement, crop, occupancy |
| `focus` | string | no | What is sharp |
| `depth_of_field` | string | no | Aperture behavior |
| `aspect_ratio` | string | yes | Output shape |

The visibility ledger is computed for this camera. If the camera changes, the ledger must change with it.

## Visibility Fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `entity_id` | string | yes | References an entity |
| `feature_id` | string | yes | References a feature in that entity |
| `surface` | string | yes | Visible surface zone at this camera |
| `state` | string | yes | `visible`, `partial`, `hidden`, `off_frame` |
| `cue` | string | yes | `direct`, `silhouette`, `shadow`, `reflection`, `transparency`, `protrusion`, `none` |
| `prompt_action` | string | yes | `describe`, `suggest`, `omit`, `negative` |
| `note` | string | no | Why the state was assigned |

A hidden or off-frame feature must not use `describe`. That is a contradiction, and the validator rejects it.

## Environment, Lighting, Color

`environment`:

| Field | Meaning |
| --- | --- |
| `location` | Place or setting |
| `time` | Time of day or narrative time |
| `weather` | Weather or atmospheric condition |
| `atmosphere` | Haze, dust, smoke, spray, stillness |
| `absent` | Things that must not appear |

`lighting`:

| Field | Meaning |
| --- | --- |
| `key` | Main source, direction, quality |
| `fill` | Bounce or ambient fill |
| `rim` | Rim or edge light, or `none` |
| `time_of_day` | Lighting time |
| `color_temperature` | Warm, cool, neutral, mixed |
| `shadows` | Direction, edge, length |

`color_finish`:

| Field | Meaning |
| --- | --- |
| `palette` | Dominant colors |
| `saturation` | Muted, natural, saturated |
| `contrast` | Low, medium, high |
| `medium` | Photoreal, illustration, 3D render, etc. |
| `grain` | Film grain, noise, clean |

## Constraints And Notes

`constraints`:

```json
{
  "must_include": ["the cracked dome"],
  "must_avoid": ["readable text", "rear winding key"],
  "exact_text": []
}
```

`assumptions` record choices made without evidence:

```json
{"claim": "camera is at chest height", "reason": "not specified; chosen for a natural view"}
```

`conflicts` record contradictions:

```json
{"claim": "case is brass and copper", "resolution": "used copper; copper appears in two later passages", "status": "resolved"}
```

Status is `open`, `resolved`, or `accepted`. An `open` conflict is a warning, not a blocker, but do not hide it.

`ignored` records non-visual material:

```json
{"info": "the instrument hums before storms", "reason": "no visible consequence in the dump"}
```

## Enums

- `mode`: `object`, `scene`
- `role`: `primary`, `secondary`, `environment`, `prop`
- `origin`: `stated`, `inferred`, `default`
- `visibility.state`: `visible`, `partial`, `hidden`, `off_frame`
- `visibility.cue`: `direct`, `silhouette`, `shadow`, `reflection`, `transparency`, `protrusion`, `none`
- `visibility.prompt_action`: `describe`, `suggest`, `omit`, `negative`
- `conflicts.status`: `open`, `resolved`, `accepted`

## Example

```json
{
  "schema_version": 1,
  "world_id": "keepers-tideclock",
  "slug": "keepers-tideclock",
  "updated": "2026-11-13",
  "mode": "object",
  "platform": "portable",
  "visual_thesis": "A weathered brass tideclock looks like a scientific heirloom, lit by a storm lantern.",
  "scale_anchors": [
    {"label": "human adult", "size": "1.7 m", "role": "comparison"},
    {"label": "wooden watch-room table", "size": "0.8 m high", "role": "support"}
  ],
  "entities": [
    {
      "id": "e1",
      "name": "Tideclock",
      "role": "primary",
      "origin": "stated",
      "geometry": "Upright drum-shaped instrument: circular glass front in a brass frame, conical iron base, three concentric rings behind the glass.",
      "dimensions": "~0.8 m tall, ~0.5 m wide, ~0.35 m deep",
      "materials": ["oxidized brass", "smoked glass", "blackened iron"],
      "colors": ["brass", "smoke gray", "iron black"],
      "finish": "satin metal with handling polish, salt pitting, dusty recesses",
      "condition": "used and maintained, not restored",
      "placement": "centered on the table, rear edge turned away from camera",
      "pose": "upright, front dome facing camera-left",
      "features": [
        {
          "id": "f1",
          "name": "front glass dome",
          "surface": "front",
          "description": "smoked glass disc in a brass bezel, faint salt film",
          "origin": "stated"
        },
        {
          "id": "f2",
          "name": "lunar ring",
          "surface": "front",
          "description": "middle brass ring with a pitted lunar disc, readable through the glass",
          "origin": "stated"
        },
        {
          "id": "f3",
          "name": "rear winding key",
          "surface": "back",
          "description": "iron key projecting from the rear case",
          "origin": "stated"
        }
      ]
    }
  ],
  "environment": {
    "location": "lighthouse watch room",
    "time": "dusk",
    "weather": "storm outside",
    "atmosphere": "damp air, faint lens haze, rain streaks on the window",
    "absent": ["people", "other instruments", "readable text"]
  },
  "camera": {
    "view_id": "front-left-three-quarter",
    "height": "1.2 m above floor",
    "distance": "2.2 m",
    "azimuth_deg": -35,
    "elevation_deg": 8,
    "lens": "50mm",
    "shot_scale": "full instrument with table edge",
    "framing": "subject centered, two-thirds of frame height",
    "focus": "front glass dome",
    "depth_of_field": "f/2.8, shallow",
    "aspect_ratio": "3:2"
  },
  "visibility": [
    {
      "entity_id": "e1",
      "feature_id": "f1",
      "surface": "front",
      "state": "visible",
      "cue": "direct",
      "prompt_action": "describe",
      "note": "facing camera, fully in frame"
    },
    {
      "entity_id": "e1",
      "feature_id": "f2",
      "surface": "front",
      "state": "visible",
      "cue": "transparency",
      "prompt_action": "describe",
      "note": "seen through the smoked glass, slightly softened"
    },
    {
      "entity_id": "e1",
      "feature_id": "f3",
      "surface": "back",
      "state": "hidden",
      "cue": "none",
      "prompt_action": "negative",
      "note": "rear of case faces away; likely to be invented"
    }
  ],
  "lighting": {
    "key": "warm oil lamp from frame upper right, soft and close",
    "fill": "cool blue storm light through the window behind",
    "rim": "thin cool rim along the left bezel",
    "time_of_day": "dusk",
    "color_temperature": "mixed warm and cool",
    "shadows": "soft, falling left and slightly behind the base"
  },
  "color_finish": {
    "palette": ["brass", "smoke gray", "sea green", "amber"],
    "saturation": "muted",
    "contrast": "medium",
    "medium": "photoreal",
    "grain": "fine film grain"
  },
  "style": "photoreal cinematic still life",
  "constraints": {
    "must_include": ["the front glass dome", "the lunar ring"],
    "must_avoid": ["readable text", "rear winding key", "extra dials"],
    "exact_text": []
  },
  "assumptions": [
    {"claim": "camera height is chest level", "reason": "not specified; chosen for a natural product view"}
  ],
  "conflicts": [],
  "ignored": [
    {"info": "the instrument hums before storms", "reason": "no visible consequence in the dump"}
  ]
}
```

## Update Semantics

- Treat records as keyed by `id`. Replace a record; do not append a second version.
- New explicit facts supersede old facts. Record the supersession in `conflicts` only when both claims remain visible in the dump or the change is material.
- When geometry changes, recompute placement, contact, occlusion, frame occupancy, and scale anchors before touching the prompt.
- When the camera changes, keep the world fixed and recompute visibility, framing, focus, and the ledger.
- When a feature is removed or retracted, delete its visibility entry and remove its positive description. Keep a negative constraint only if the model would still invent it.
- When the world identity changes, rebuild the state. Do not patch a different object into an old reconstruction.
- Increment the prompt version in the prompt file header and note the material change.

## Validation

Run:

```bash
python scripts/scene_state.py validate image-scenes/<slug>/scene-state.json
```

The validator checks required fields, enum values, unique IDs, visibility references, and contradictions such as a hidden feature marked `describe`. It does not judge whether the reconstruction is good.

Generate a readable reconstruction brief:

```bash
python scripts/scene_state.py brief image-scenes/<slug>/scene-state.json
```

Compare an update:

```bash
python scripts/scene_state.py diff image-scenes/<slug>/scene-state.old.json image-scenes/<slug>/scene-state.json
```

Check a prompt against the state:

```bash
python scripts/scene_state.py check --state image-scenes/<slug>/scene-state.json --file image-scenes/<slug>/prompt.md
```

## Keeping The State Compact

Track a feature only when it is visible, partially visible, hidden but silhouette- or cue-relevant, or likely to be invented by the model. Merge duplicates. Do not store the raw dump, long quotations, or non-visual lore unless it explains a visible decision. A state that is too large to update reliably is worse than a small state that is accurate.
