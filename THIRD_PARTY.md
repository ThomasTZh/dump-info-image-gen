# Third-party software and attribution

No upstream code, text, or binary is included in this repository. The skill instructions, references, helper, templates, tests, and documentation are original.

## Host and dependencies

| Component | Role here | Project | Licence | Distribution |
| --- | --- | --- | --- | --- |
| Agent Skills specification | Front matter and discovery format followed by the skill | <https://agentskills.io/specification> | specification, not software | referenced only |
| DeepSeek Harness | Host that discovers and loads the skill | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | MIT | installed separately |
| Python | Runtime for the helper and tests | [python/cpython](https://github.com/python/cpython) | PSF-2.0 | installed separately |
| Git | Installation and version control | [git/git](https://github.com/git/git) | GPL-2.0 | installed separately |
| PyYAML | YAML parser used by the optional skill validator | [yaml/pyyaml](https://github.com/yaml/pyyaml) | MIT | installed separately |
| `directing-image-prompts` | Optional companion skill for prompt polishing and linting | [Nanoleava/directing-image-prompts](https://github.com/Nanoleava/directing-image-prompts) | No licence declared upstream | installed separately, not bundled |

## Copyright and licence compliance

- **Original files:** the MIT [`LICENSE`](LICENSE) covers `SKILL.md`, the files under `references/`, `scripts/`, `assets/`, `agents/`, `tests/`, `README.md`, and `THIRD_PARTY.md`.
- **Upstream notices:** none are redistributed, because no upstream file is present here.
- **Unresolved:** none. If a future change copies an upstream file, its project, exact revision, retained notice, and licence must be added to this file before the change is published.
