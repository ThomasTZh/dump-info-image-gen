# dump-info-image-gen

This repository holds written instructions that help an assistant turn a large pile of notes about an object or a place into a request for a picture. It works out the shape and position of the thing, decides where the viewer stands, and keeps only the parts that would actually be in view. When new notes arrive, it works the scene out again and writes a fresh request instead of patching the old one.

## Purpose and gaps

Most picture-prompt guidance starts from a clean brief. Real source material is not clean: a dump may mix measurements, history, contradictions, details on the back of an object, and facts that have no visible effect. A request that lists all of it is not the same as a picture that one camera can see.

The skill adds the missing steps. It sorts the notes, builds a persistent description of the object or scene, chooses a camera, marks every tracked feature as visible, partial, hidden, or outside the frame, and writes only the visible set. Each new dump triggers a rebuild, so a later correction cannot leave an old detail in the request.

## Features

- **Note sorting:** separates what changes pixels, what shapes the object, what is only story, what conflicts, and what is missing.
- **Persistent scene plan:** keeps entities, size, materials, placement, light, scale, and one camera position in a JSON state file.
- **Visibility check:** records each feature as `visible`, `partial`, `hidden`, or `off_frame`, with an optional cue such as silhouette, shadow, reflection, or transparency.
- **Visible-only request:** writes from the camera's view and uses the negative list only for parts the image model is likely to invent.
- **Rebuild loop:** a new dump updates the state, recomputes visibility, and rewrites the request. Story notes with no visible effect do not force a fake visual change.
- **Several views:** one world model, several cameras, one request per view.
- **Helper script:** `scene_state.py` initializes, validates, renders a brief, compares two states, and checks a prompt for hidden-feature leaks.
- **Templates and tests:** startable JSON and Markdown templates, plus 13 standard-library unit tests.

## Not for / limitations

- **Not an image generator.** It writes requests for an image model; it does not run one.
- **Not a general prompt polisher.** For a clean prompt with no source dump, use the companion `directing-image-prompts` skill.
- **Reasoned visibility, not measured 3D geometry.** The camera and occlusion model is a careful description, not a mesh renderer. Complex geometry can need manual correction.
- **No image-quality evidence.** No image model was run for this release, so whether a particular model renders the request well is untested.
- **The source notes are taken as evidence.** The skill does not check whether the notes are true.
- **Automatic skill selection is untested.** Whether an assistant chooses this skill from its description depends on the assistant and the request.
- **POSIX examples.** The install and uninstall commands assume a Linux or macOS shell.
- **Python 3.9 or newer.** Verified on Python 3.14.8. Older versions were not tested. The helper and tests use only the standard library; PyYAML is needed only for the optional skill validator.

## Reproduction environment

| Component | Requirement |
| --- | --- |
| Operating system | Nobara Linux 44, kernel 7.3.4, KDE Plasma on Wayland |
| Runtime | Python 3.14.8, standard library only |
| Harness | DeepSeek Harness 0.2.1-rc.2, for skill discovery |
| Tools | Git; PyYAML for the optional skill validator |
| Hardware | None beyond a desktop |
| Input | The cloned repository; no external data or network service |

## Install and run

```bash
LOCAL_AI=${LOCAL_AI:-$HOME/.config/local-ai}
mkdir -p "$HOME/.agents/skills" "$LOCAL_AI/skills/on-request"
git clone https://github.com/ThomasTZh/dump-info-image-gen \
  "$HOME/.agents/skills/dump-info-image-gen"
ln -sfn "$HOME/.agents/skills/dump-info-image-gen" \
  "$LOCAL_AI/skills/on-request/dump-info-image-gen"
```

Expected output: the harness lists a `dump-info-image-gen` skill. Ask it to turn a dump into a picture request; the skill loads from [`SKILL.md`](SKILL.md) and reads the references and templates it needs.

The helper can be checked without the harness:

```bash
python3 "$HOME/.agents/skills/dump-info-image-gen/scripts/scene_state.py" \
  validate "$HOME/.agents/skills/dump-info-image-gen/assets/templates/scene-state.json"
```

Expected output:

```text
OK: .../assets/templates/scene-state.json (mode=object view=front-three-quarter entities=1 features=1 visibility=1)
```

A first project state can be started with:

```bash
python3 "$HOME/.agents/skills/dump-info-image-gen/scripts/scene_state.py" \
  init --out image-scenes/demo/scene-state.json --slug demo --mode object
```

The generated file is a scaffold. Replace the placeholder values, then run `validate` and `brief` before writing the picture request.

## Uninstall

```bash
LOCAL_AI=${LOCAL_AI:-$HOME/.config/local-ai}
rm -f "$LOCAL_AI/skills/on-request/dump-info-image-gen"
rm -rf "$HOME/.agents/skills/dump-info-image-gen"
```

The state and prompt files under `image-scenes/` are deliberately left in place.

## Layout

| Component | Path | Contents | Class |
| --- | --- | --- | --- |
| Skill method | `SKILL.md` | When to use the skill, the five-pass workflow, hard rules, state layout, and quality gate | Original |
| Intake and triage | `references/intake-and-triage.md` | Claim classes, relevance tests, contradiction rules, retractions, and gap policy | Original |
| Reconstruction | `references/reconstruction.md` | Object and scene model, scale, materials, light, update semantics, consistency checks | Original |
| Camera and visibility | `references/camera-and-visibility.md` | Camera station, surface facing, occlusion, visibility states, cues, multi-view rules | Original |
| State schema | `references/scene-state.md` | JSON fields, enums, file layout, example, and validation rules | Original |
| Prompt synthesis | `references/prompt-synthesis.md` | State-to-request mapping, visible and partial phrasing, negatives, length, anti-patterns | Original |
| Platform profiles | `references/platform-profiles.md` | Portable, Midjourney, Stable Diffusion, OpenAI, and general web formatting | Original |
| Audit rubric | `references/audit-rubric.md` | Reconstruction, prompt, update, and cross-view checks | Original |
| Worked examples | `references/examples.md` | A full object dump, correction, state diff, and prompt rewrite; a scene layout conflict | Original |
| State helper | `scripts/scene_state.py` | `init`, `validate`, `brief`, `diff`, and `check` commands | Original |
| Templates | `assets/templates/` | State skeleton, intake ledger, and update report | Original |
| Agent metadata | `agents/openai.yaml` | Optional display name, short description, and default prompt | Original |
| Tests | `tests/test_scene_state.py` | 13 tests for state validation, briefs, diffs, and prompt checks | Original |
| Documentation | `README.md`, `THIRD_PARTY.md` | This page and the attribution record | Original |
| Licence | `LICENSE` | MIT, covering the original files only | Original |
| Agent Skills specification | none | Front matter and discovery format followed by the skill [1] | Third-party |
| DeepSeek Harness | none | Host that discovers and loads the skill [2] | Third-party |
| Python, Git, PyYAML | none | Runtime and verification tools, not bundled [4] | Third-party |
| `directing-image-prompts` | none | Optional companion for prompt polishing and linting; not bundled [3] | Third-party |

No upstream code, text, or binary is copied into this repository.

## Results

| Check | Command | Result |
| --- | --- | --- |
| Front matter and naming | `python3 .../quick_validate.py .` | pass: `Skill is valid!` |
| Unit tests | `python3 -m unittest discover -s tests -v` | pass: 13 tests, 0 failures |
| Script compiles | `python3 -m py_compile scripts/scene_state.py` | pass |
| Template state | `python3 scripts/scene_state.py validate assets/templates/scene-state.json` | pass: `OK`, 1 entity, 1 feature, 1 visibility entry |
| CLI init and brief | `init` to a temporary path, then `validate` and `brief` | pass: valid scaffold and rendered brief |
| Hidden-feature check | `check` with a hidden feature named in the visible prompt | pass: exits 1 and names the hidden feature |
| Visible prompt check | `check` with the hidden feature only in the negative list | pass: exits 0 |
| Privacy scan | search tracked files for absolute home paths and token-shaped strings | pass: clean |

**Not tested:** image generation from the produced request, automatic skill selection by a model, Windows, Python 3.9 specifically, and large real-world dumps beyond the worked examples.

## Acknowledgements

- The Agent Skills specification [1] defines the front matter and discovery shape this skill follows.
- DeepSeek Harness [2] is the host used to check discovery and loading.
- `directing-image-prompts` [3] is the companion skill for prompt polishing and the optional prompt linter. No files or text are copied from it.
- Python's standard library [4] provides the helper's JSON, file, subprocess, and test primitives.

## References

1. Agent Skills specification. <https://agentskills.io/specification>.
2. DeepSeek Harness. <https://github.com/deepseek-ai/deepseek-harness>. MIT.
3. `directing-image-prompts`. <https://github.com/Nanoleava/directing-image-prompts>. No licence declared upstream; optional companion, installed separately.
4. Python. <https://github.com/python/cpython>. PSF-2.0.

## Licenses

- **Original files:** `SKILL.md`, the files under `references/`, `scripts/`, `assets/`, `agents/`, `tests/`, `README.md`, and `THIRD_PARTY.md` are covered by the MIT [`LICENSE`](LICENSE), copyright 2026 Thomas.
- **Third-party components:** none are redistributed. The specification, host, runtime, and companion skill listed above keep their own terms; see [`THIRD_PARTY.md`](THIRD_PARTY.md).
- **Installed separately:** Python, Git, PyYAML, DeepSeek Harness, and `directing-image-prompts` are not bundled.
