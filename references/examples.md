# Examples

Read this for a complete dump, reconstruction, prompt, and update cycle.

## Example 1: Object With A Hidden Rear

### Initial Dump

```text
The Keeper's Tideclock. A portable tidal predictor made by the Meridian Guild about four hundred years ago. It is 0.8 meters tall, 0.5 meters wide, and 0.35 meters deep. The frame is oxidized brass, the front dome is smoked glass, and the base is blackened iron. Inside the glass are three concentric rings: the outer ring has twelve shallow engraved tide marks, the middle ring carries a pitted lunar disc, and the inner ring holds a thin mercury vial. There is a rectangular repair plate riveted to the left side. A folding carrying handle is attached to the right side. A winding key projects from the rear, and the escapement is sealed inside the case. The whole thing is salt-crusted and has been repaired more than once. It sits on a scarred wooden table in a lighthouse watch room at dusk, with a storm outside and an oil lamp burning to the right. The keeper says it hums before storms and smells faintly of ozone. The guild motto is "The sea keeps time," engraved on the inner back plate. We see it from a person standing at the table, slightly to its left.
```

### Intake

| Claim | Class | Decision |
| --- | --- | --- |
| 0.8 m tall, 0.5 m wide, 0.35 m deep | V | Stated dimensions; use as scale |
| Oxidized brass, smoked glass, blackened iron | V | Stated materials |
| Three rings, tide marks, lunar disc, mercury vial | V | Visible through the front dome |
| Left repair plate | V | Visible from the chosen left-of-front view |
| Right carrying handle | S | Likely off-frame at this crop |
| Rear winding key | S | Hidden; negative prompt |
| Internal escapement | S | Hidden; negative prompt |
| Guild motto on inner back plate | S | Hidden; not readable in this view |
| "Hums before storms", "smells of ozone" | N | No visible consequence; ignored |
| "Four hundred years old" | I | Render wear only; do not assert age |
| "As seen from a person standing at the table, slightly to its left" | R | Camera constraint: front-left, human height |

No blocking conflict. The camera is implied, so no question is needed.

### Reconstruction Summary

```text
Thesis: a weathered scientific heirloom, warm lamp light against a cold storm.
View: front-left three-quarter, camera at 1.3 m, distance 1.8 m, 50mm, slightly above the table.
Visible: front glass dome, lunar ring and tide marks through the glass, left repair plate, front and left of the brass case, blackened base.
Partial: engraved tide marks are softened by the smoked glass; the right side and handle are at the frame edge.
Hidden: rear winding key, internal escapement, inner back plate with the motto.
Ignored: the hum and the ozone smell; age is expressed as handling wear, not as a label.
Scale: the table edge and a 0.8 m height against a waist-high table.
```

### Visibility Ledger

| Feature | State | Cue | Action |
| --- | --- | --- | --- |
| Front glass dome | visible | direct | describe |
| Lunar ring | visible | transparency | describe |
| Tide marks | partial | transparency | suggest |
| Left repair plate | visible | direct | describe |
| Blackened base | visible | direct | describe |
| Right carrying handle | off_frame | none | omit |
| Rear winding key | hidden | none | negative |
| Internal escapement | hidden | none | negative |
| Guild motto on inner back plate | hidden | none | negative |

### Initial Prompt

```text
Photoreal cinematic still life, 50mm lens at chest height, three-quarter front-left view, the instrument centered and filling two-thirds of the frame. A waist-high tideclock stands on a scarred wooden watch-room table: an oxidized brass drum with a smoked-glass front dome, its bezel edges polished by handling and its recesses salt-pitted. Through the glass, three concentric brass rings: the outer carries shallow engraved tide marks, the middle a pitted lunar disc, the inner a thin sealed mercury column. A mismatched rectangular repair plate is riveted to the left side of the case, slightly warmer in tone than the surrounding brass. The front and left side face the viewer. Behind it, a rain-streaked lighthouse window at dusk, cold blue-gray storm light outside, a warm oil-lamp key from the upper right, a faint reflection on the dome, and a soft contact shadow under the blackened iron base. Muted brass, smoke gray, sea green, amber; fine film grain. Negative: no readable text, no guild mark, no rear winding key, no visible internal mechanism, no extra dials, no glossy new brass.
```

Why it works: the hidden rear mechanism and motto stay out of the positive prompt; the left plate is visible because the camera is left of front; the warm lamp and cold window establish the mood without lore.

### New Dump

```text
Correction: the case is oxidized copper, not brass. The repair plate is on the rear-left panel, not the left side, and it carries the guild stamp. The mercury vial was a misremembering; it is a sealed alcohol column with a small bubble. The lunar disc is a crescent cutout, not a full disc. There is a hairline crack across the upper left of the glass dome. The base is green-patinated bronze, not blackened iron. It is dawn now, the storm has passed, and the lamp is out; light comes from the window. The camera is slightly above the instrument, looking down about 20 degrees.
```

### Update Diff

```text
Changed: brass -> oxidized copper; black iron base -> green-patinated bronze; full lunar disc -> crescent cutout; mercury vial -> sealed alcohol column with bubble; dusk storm + lamp -> dawn, storm passed, no lamp; camera elevation 8 -> 20 degrees.
Moved: left repair plate -> rear-left panel; now hidden at this view. Guild stamp is also hidden.
Added: hairline crack across the upper-left dome.
Removed: mercury vial (retracted).
Newly visible: top of the case, upper dome crack, stronger top-surface light.
Newly hidden: left repair plate, guild stamp.
Prompt effect: the plate and stamp leave the positive prompt and enter the negative; the light and palette shift; the crescent and alcohol column replace the full disc and mercury; the camera tilt exposes the top.
```

### Updated Prompt

```text
Photoreal cinematic still life at dawn, 50mm lens from slightly above, camera tilted down about 20 degrees, three-quarter front-left view, the instrument centered and filling two-thirds of the frame. A waist-high tideclock stands on a scarred wooden watch-room table: an oxidized copper drum on a green-patinated bronze base, the copper bezel edges polished by handling and the recesses salt-pitted. A hairline crack runs across the upper left of the smoked-glass dome. Through the glass, three concentric rings: the outer carries shallow engraved tide marks, the middle a crescent cutout, the inner a sealed alcohol column with a small bubble. The front, left side, and top of the case face the viewer. Behind it, a rain-washed lighthouse window at dawn, pale cool light from frame left, soft shadows falling right, a thin cool reflection on the dome, and a soft contact shadow under the bronze base. Muted copper, green patina, smoke gray, pale blue; fine film grain. Negative: no readable text, no guild stamp, no rear repair plate, no rear winding key, no visible internal mechanism, no mercury, no extra dials, no warm lamp light, no glossy new copper.
```

This is a rebuild, not an edit. The old plate sentence is gone because the plate is now hidden, and the old lamp light is gone because the scene time changed.

## Example 2: Scene With Conflicting Layout

### Initial Dump

```text
An abandoned brutalist reading hall, three gallery levels around a central void, flooded up to the second floor. The glass roof is shattered and rain is coming in. Thousands of swollen books. No people. Dawn fog. Camera from the mezzanine, looking down across the water. The order that built it was obsessed with catalogues; every pillar is numbered. The flood came after the roof failed.
```

### New Dump

```text
Correction: the hall has four gallery levels, not three. The water is only about 1.2 meters deep and does not reach the first gallery. The glass roof is intact but filthy, not shattered. The camera is at water level looking up toward the roof, not from the mezzanine.
```

### What Changes

- Three levels become four: the vertical rhythm, railing count, and visible ceiling height all change.
- "Flooded to the second floor" becomes 1.2 m of water: the first gallery is dry, the waterline is low, and reflections show pillars rather than a submerged upper level.
- Shattered roof and rain become an intact dirty roof: no rain shafts, no broken glass; the light is a diffuse, dirty skylight.
- Camera moves from mezzanine-down to water-level-up: the composition now includes the roof, the underside of the galleries, the waterline, and the pillars rising out of the water. The mezzanine view disappears.
- The catalogue lore and pillar numbers remain non-visual unless a pillar number is readable at the new distance. It is not, so the prompt omits it.

### Updated Prompt Sketch

```text
Photoreal architectural interior, water-level camera with a slight upward tilt, 24mm lens, four concrete gallery levels ringing a central void. The bottom of the frame is dark floodwater about waist-deep, its surface broken by slow ripples and reflecting the pillars; the first gallery is above the waterline and dry. Four tiers of weathered concrete walkways recede upward, their railings simplified by distance, converging toward a filthy glass roof that diffuses pale dawn light. No people, no shattered glass, no rain shafts, no readable signs or catalogue numbers. Cold gray-green palette, damp concrete, soft contrast, fine haze, subtle film grain. Negative: no people, no broken roof, no rain, no text, no floating books in the foreground.
```

The prompt rebuild reflects all four corrections. Appending "also the roof is intact" to the old prompt would have left the rain and the mezzanine view in place.
