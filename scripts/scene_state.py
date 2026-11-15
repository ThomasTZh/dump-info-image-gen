#!/usr/bin/env python3
"""Initialize, validate, brief, diff, and check dump-info image scene states."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "templates" / "scene-state.json"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MODES = {"object", "scene"}
ROLES = {"primary", "secondary", "environment", "prop"}
ORIGINS = {"stated", "inferred", "default"}
VIS_STATES = {"visible", "partial", "hidden", "off_frame"}
CUES = {"direct", "silhouette", "shadow", "reflection", "transparency", "protrusion", "none"}
PROMPT_ACTIONS = {"describe", "suggest", "omit", "negative"}
CONFLICT_STATUSES = {"open", "resolved", "accepted"}

GENERIC_FEATURE_NAMES = {
    "feature",
    "features",
    "detail",
    "details",
    "part",
    "parts",
    "surface",
    "primary subject",
    "distinctive feature",
}

CAMERA_PATTERNS = [
    r"\bcamera\b",
    r"\blens\b",
    r"\b\d{2,3}\s?mm\b",
    r"\bwide[- ]angle\b",
    r"\btelephoto\b",
    r"\bmacro\b",
    r"\b(?:low|high)[- ]angle\b",
    r"\beye[- ]level\b",
    r"\boverhead\b",
    r"\btop[- ]down\b",
    r"\bthree[- ]quarter\b",
    r"\bprofile\b",
    r"\bview\b",
    r"\bframing\b",
    r"\bshot\b",
    r"\bdepth of field\b",
    r"\bfocus(?:ed|es|ing)?\b",
    r"\bperspective\b",
    r"\btilt(?:ed)?\b",
    r"\bazimuth\b",
    r"\belevation\b",
]

LIGHT_PATTERNS = [
    r"\blight(?:ing)?\b",
    r"\blit\b",
    r"\bsun(?:light)?\b",
    r"\bshadow",
    r"\bglow",
    r"\blamp\b",
    r"\bdawn\b",
    r"\bdusk\b",
    r"\bbacklight",
    r"\brim light\b",
    r"\bkey light\b",
    r"\bambient\b",
    r"\bexposure\b",
    r"\breflection\b",
    r"\bcandle",
    r"\bfirelight\b",
    r"\bmoonlight\b",
]

COMPOSITION_PATTERNS = [
    r"\bcomposition\b",
    r"\bframe\b",
    r"\bforeground\b",
    r"\bmidground\b",
    r"\bbackground\b",
    r"\bcenter(?:ed)?\b",
    r"\bleft\b",
    r"\bright\b",
    r"\btop\b",
    r"\bbottom\b",
    r"\bnegative space\b",
    r"\bthirds?\b",
    r"\bfills?\b",
    r"\boccup(?:y|ies|ying)\b",
    r"\bcrop(?:ped)?\b",
]

STATE_TERMS = [
    "visibility ledger",
    "prompt_action",
    "entity_id",
    "schema_version",
    "reconstruction brief",
    "state file",
]

NEGATION_RE = re.compile(
    r"(?:\bno\b|\bnot\b|\bwithout\b|\bavoid\b|\bexclude(?:s|d)?\b|\bfree of\b|"
    r"\babsence of\b|\bdo not\b|\bdon't\b|\bmust not\b|\bnever\b)"
    r"(?:\s+(?:the|a|an|any|include|show|render|add|depict|have|contain|feature|"
    r"visible|readable|additional|extra|other))*\s*$",
    re.IGNORECASE,
)

STABLE_DIFFUSION_PLATFORMS = {"stable-diffusion", "sd", "sdxl", "flux"}


class StateError(Exception):
    """A user-facing state or file error."""


def load_json(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise StateError(f"file not found: {path}") from exc
    except OSError as exc:
        raise StateError(f"cannot read {path}: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StateError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise StateError(f"{path}: state must be a JSON object")
    return data


def _require_str(obj: dict, key: str, path: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key}: expected a non-empty string")
        return None
    return value.strip()


def _optional_str(obj: dict, key: str, path: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{path}.{key}: expected a string")
        return None
    return value


def _require_list(obj: dict, key: str, path: str, errors: list[str]) -> list | None:
    value = obj.get(key)
    if not isinstance(value, list):
        errors.append(f"{path}.{key}: expected an array")
        return None
    return value


def _require_number(obj: dict, key: str, path: str, errors: list[str]) -> float | None:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path}.{key}: expected a number")
        return None
    return float(value)


def _string_list(value, path: str, errors: list[str], required: bool = False) -> list[str]:
    if value is None:
        if required:
            errors.append(f"{path}: expected an array of strings")
        return []
    if not isinstance(value, list):
        errors.append(f"{path}: expected an array of strings")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            errors.append(f"{path}[{index}]: expected a string")
            continue
        result.append(item)
    return result


def _dict_list(value, path: str, errors: list[str]) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        errors.append(f"{path}: expected an array")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{path}[{index}]: expected an object")
            continue
        result.append(item)
    return result


def validate_state(state: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors block use; warnings need review."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(state, dict):
        return ["state: expected a JSON object"], warnings

    version = state.get("schema_version")
    if version != SCHEMA_VERSION:
        errors.append(f"schema_version: expected {SCHEMA_VERSION}, got {version!r}")

    slug = _require_str(state, "slug", "state", errors)
    if slug and not SLUG_RE.match(slug):
        errors.append("slug: use lowercase letters, digits, and single hyphens")

    world_id = state.get("world_id")
    if world_id is not None and (not isinstance(world_id, str) or not world_id.strip()):
        errors.append("world_id: expected a non-empty string when present")

    updated = _require_str(state, "updated", "state", errors)
    if updated and not DATE_RE.match(updated):
        errors.append("updated: expected an ISO date YYYY-MM-DD")

    mode = _require_str(state, "mode", "state", errors)
    if mode and mode not in MODES:
        errors.append(f"mode: expected one of {sorted(MODES)}")

    _require_str(state, "platform", "state", errors)
    _require_str(state, "visual_thesis", "state", errors)
    _require_str(state, "style", "state", errors)

    anchors = _dict_list(state.get("scale_anchors"), "scale_anchors", errors)
    if not anchors:
        warnings.append("scale_anchors: no scale anchor; size may be unproven in the image")
    for index, anchor in enumerate(anchors):
        path = f"scale_anchors[{index}]"
        _require_str(anchor, "label", path, errors)
        _optional_str(anchor, "size", path, errors)
        _optional_str(anchor, "role", path, errors)

    entities = state.get("entities")
    if not isinstance(entities, list) or not entities:
        errors.append("entities: expected a non-empty array")
        entities = []

    entity_ids: set[str] = set()
    feature_index: dict[tuple[str, str], dict] = {}
    primary_features: set[tuple[str, str]] = set()

    for entity_index, entity in enumerate(entities):
        path = f"entities[{entity_index}]"
        if not isinstance(entity, dict):
            errors.append(f"{path}: expected an object")
            continue

        entity_id = _require_str(entity, "id", path, errors)
        if entity_id:
            if entity_id in entity_ids:
                errors.append(f"{path}.id: duplicate entity id {entity_id!r}")
            entity_ids.add(entity_id)

        _require_str(entity, "name", path, errors)
        role = _require_str(entity, "role", path, errors)
        if role and role not in ROLES:
            errors.append(f"{path}.role: expected one of {sorted(ROLES)}")
        origin = _require_str(entity, "origin", path, errors)
        if origin and origin not in ORIGINS:
            errors.append(f"{path}.origin: expected one of {sorted(ORIGINS)}")
        _require_str(entity, "geometry", path, errors)

        for key in ("dimensions", "finish", "condition", "placement", "pose"):
            _optional_str(entity, key, path, errors)

        _string_list(entity.get("materials"), f"{path}.materials", errors)
        _string_list(entity.get("colors"), f"{path}.colors", errors)

        features = entity.get("features")
        if not isinstance(features, list):
            errors.append(f"{path}.features: expected an array")
            features = []

        feature_ids: set[str] = set()
        for feature_pos, feature in enumerate(features):
            feature_path = f"{path}.features[{feature_pos}]"
            if not isinstance(feature, dict):
                errors.append(f"{feature_path}: expected an object")
                continue

            feature_id = _require_str(feature, "id", feature_path, errors)
            if feature_id:
                if feature_id in feature_ids:
                    errors.append(f"{feature_path}.id: duplicate feature id {feature_id!r}")
                feature_ids.add(feature_id)

            _require_str(feature, "name", feature_path, errors)
            _require_str(feature, "surface", feature_path, errors)
            _require_str(feature, "description", feature_path, errors)
            feature_origin = _require_str(feature, "origin", feature_path, errors)
            if feature_origin and feature_origin not in ORIGINS:
                errors.append(f"{feature_path}.origin: expected one of {sorted(ORIGINS)}")

            if entity_id and feature_id:
                feature_index[(entity_id, feature_id)] = feature
                if role == "primary":
                    primary_features.add((entity_id, feature_id))

    environment = state.get("environment")
    if not isinstance(environment, dict):
        errors.append("environment: expected an object")
        environment = {}
    for key in ("location", "time", "weather", "atmosphere"):
        _require_str(environment, key, "environment", errors)
    _string_list(environment.get("absent"), "environment.absent", errors)

    camera = state.get("camera")
    if not isinstance(camera, dict):
        errors.append("camera: expected an object")
        camera = {}
    for key in ("view_id", "height", "distance", "lens", "shot_scale", "framing", "aspect_ratio"):
        _require_str(camera, key, "camera", errors)
    for key in ("focus", "depth_of_field"):
        _optional_str(camera, key, "camera", errors)

    azimuth = _require_number(camera, "azimuth_deg", "camera", errors)
    if azimuth is not None and not -360 <= azimuth <= 360:
        errors.append("camera.azimuth_deg: expected a value between -360 and 360")
    elevation = _require_number(camera, "elevation_deg", "camera", errors)
    if elevation is not None and not -90 <= elevation <= 90:
        errors.append("camera.elevation_deg: expected a value between -90 and 90")

    visibility = state.get("visibility")
    if not isinstance(visibility, list):
        errors.append("visibility: expected an array")
        visibility = []

    seen_visibility: set[tuple[str, str]] = set()
    for index, entry in enumerate(visibility):
        path = f"visibility[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{path}: expected an object")
            continue

        entity_id = _require_str(entry, "entity_id", path, errors)
        feature_id = _require_str(entry, "feature_id", path, errors)
        _require_str(entry, "surface", path, errors)

        state_value = _require_str(entry, "state", path, errors)
        if state_value and state_value not in VIS_STATES:
            errors.append(f"{path}.state: expected one of {sorted(VIS_STATES)}")

        cue = _require_str(entry, "cue", path, errors)
        if cue and cue not in CUES:
            errors.append(f"{path}.cue: expected one of {sorted(CUES)}")

        action = _require_str(entry, "prompt_action", path, errors)
        if action and action not in PROMPT_ACTIONS:
            errors.append(f"{path}.prompt_action: expected one of {sorted(PROMPT_ACTIONS)}")

        _optional_str(entry, "note", path, errors)

        if entity_id and feature_id:
            key = (entity_id, feature_id)
            if key not in feature_index:
                errors.append(
                    f"{path}: references missing feature {entity_id}/{feature_id}"
                )
            if key in seen_visibility:
                errors.append(f"{path}: duplicate visibility entry for {entity_id}/{feature_id}")
            seen_visibility.add(key)

            if state_value in {"hidden", "off_frame"} and action == "describe":
                errors.append(
                    f"{path}: {state_value} feature cannot use prompt_action 'describe'"
                )
            if state_value in {"visible", "partial"} and action == "negative":
                warnings.append(
                    f"{path}: visible feature {entity_id}/{feature_id} is marked negative"
                )

    for entity_id, feature_id in sorted(primary_features):
        if (entity_id, feature_id) not in seen_visibility:
            warnings.append(
                f"visibility: primary feature {entity_id}/{feature_id} has no visibility entry"
            )

    lighting = state.get("lighting")
    if not isinstance(lighting, dict):
        errors.append("lighting: expected an object")
        lighting = {}
    for key in ("key", "time_of_day", "color_temperature", "shadows"):
        _require_str(lighting, key, "lighting", errors)
    for key in ("fill", "rim"):
        _optional_str(lighting, key, "lighting", errors)

    color_finish = state.get("color_finish")
    if not isinstance(color_finish, dict):
        errors.append("color_finish: expected an object")
        color_finish = {}
    _require_str(color_finish, "medium", "color_finish", errors)
    palette = _string_list(color_finish.get("palette"), "color_finish.palette", errors, required=True)
    if not palette:
        warnings.append("color_finish.palette: no palette entries")
    for key in ("saturation", "contrast", "grain"):
        _optional_str(color_finish, key, "color_finish", errors)

    constraints = state.get("constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints: expected an object")
        constraints = {}
    for key in ("must_include", "must_avoid", "exact_text"):
        _string_list(constraints.get(key), f"constraints.{key}", errors)

    assumptions = state.get("assumptions")
    if assumptions is not None:
        if not isinstance(assumptions, list):
            errors.append("assumptions: expected an array")
        else:
            for index, item in enumerate(assumptions):
                path = f"assumptions[{index}]"
                if isinstance(item, str):
                    if not item.strip():
                        errors.append(f"{path}: expected a non-empty string")
                elif isinstance(item, dict):
                    _require_str(item, "claim", path, errors)
                    _optional_str(item, "reason", path, errors)
                else:
                    errors.append(f"{path}: expected a string or object")

    conflicts = _dict_list(state.get("conflicts"), "conflicts", errors)
    for index, conflict in enumerate(conflicts):
        path = f"conflicts[{index}]"
        _require_str(conflict, "claim", path, errors)
        _require_str(conflict, "resolution", path, errors)
        status = _require_str(conflict, "status", path, errors)
        if status and status not in CONFLICT_STATUSES:
            errors.append(f"{path}.status: expected one of {sorted(CONFLICT_STATUSES)}")
        if status == "open":
            warnings.append(f"{path}: conflict is still open")

    ignored = state.get("ignored")
    if ignored is not None:
        if not isinstance(ignored, list):
            errors.append("ignored: expected an array")
        else:
            for index, item in enumerate(ignored):
                path = f"ignored[{index}]"
                if isinstance(item, str):
                    if not item.strip():
                        errors.append(f"{path}: expected a non-empty string")
                elif isinstance(item, dict):
                    _require_str(item, "info", path, errors)
                    _optional_str(item, "reason", path, errors)
                else:
                    errors.append(f"{path}: expected a string or object")

    return errors, warnings


def state_summary(state: dict) -> str:
    camera = state.get("camera") if isinstance(state.get("camera"), dict) else {}
    entities = state.get("entities") if isinstance(state.get("entities"), list) else []
    features = sum(
        len(entity.get("features", []))
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("features"), list)
    )
    visibility = state.get("visibility") if isinstance(state.get("visibility"), list) else []
    return (
        f"mode={state.get('mode', '?')} "
        f"view={camera.get('view_id', '?')} "
        f"entities={len(entities)} "
        f"features={features} "
        f"visibility={len(visibility)}"
    )


def _compact(value) -> str:
    if isinstance(value, list):
        return ", ".join(_compact(item) for item in value) or "none"
    if isinstance(value, dict):
        return "; ".join(f"{key}={_compact(item)}" for key, item in value.items()) or "none"
    if value is None:
        return "none"
    return str(value)


def _cell(value) -> str:
    return _compact(value).replace("|", "\\|").replace("\n", " ")


def _optional_line(lines: list[str], label: str, value) -> None:
    if value:
        lines.append(f"- {label}: {_compact(value)}")


def _feature_name(feature: dict | None) -> str:
    return _compact(feature.get("name")) if isinstance(feature, dict) else "?"


def build_brief(state: dict, warnings: list[str]) -> str:
    camera = state.get("camera") if isinstance(state.get("camera"), dict) else {}
    entities = state.get("entities") if isinstance(state.get("entities"), list) else []
    visibility = state.get("visibility") if isinstance(state.get("visibility"), list) else []
    vis_map = {
        (entry.get("entity_id"), entry.get("feature_id")): entry
        for entry in visibility
        if isinstance(entry, dict)
    }

    lines = [
        f"# Reconstruction Brief: {state.get('slug', '?')}",
        "",
        f"Thesis: {_compact(state.get('visual_thesis'))}",
        f"Mode: {state.get('mode', '?')} | Platform: {state.get('platform', '?')} | Updated: {state.get('updated', '?')}",
        "",
        "## Camera",
        f"- View: {_compact(camera.get('view_id'))}",
        f"- Height: {_compact(camera.get('height'))}",
        f"- Distance: {_compact(camera.get('distance'))}",
        f"- Azimuth: {_compact(camera.get('azimuth_deg'))} degrees",
        f"- Elevation: {_compact(camera.get('elevation_deg'))} degrees",
        f"- Lens: {_compact(camera.get('lens'))}",
        f"- Shot scale: {_compact(camera.get('shot_scale'))}",
        f"- Framing: {_compact(camera.get('framing'))}",
        f"- Focus: {_compact(camera.get('focus'))}",
        f"- Depth of field: {_compact(camera.get('depth_of_field'))}",
        f"- Aspect ratio: {_compact(camera.get('aspect_ratio'))}",
        "",
        "## Scale Anchors",
    ]
    anchors = state.get("scale_anchors") if isinstance(state.get("scale_anchors"), list) else []
    if anchors:
        for anchor in anchors:
            if not isinstance(anchor, dict):
                continue
            label = _compact(anchor.get("label"))
            size = _compact(anchor.get("size"))
            role = _compact(anchor.get("role"))
            lines.append(f"- {label}: {size} ({role})")
    else:
        lines.append("- none")

    lines.extend(["", "## Entities"])
    feature_lookup: dict[tuple[str, str], dict] = {}
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_id = entity.get("id", "?")
        lines.append("")
        lines.append(f"### {entity_id}: {_compact(entity.get('name'))}")
        lines.append(
            f"Role: {_compact(entity.get('role'))} | Origin: {_compact(entity.get('origin'))}"
        )
        _optional_line(lines, "Geometry", entity.get("geometry"))
        _optional_line(lines, "Dimensions", entity.get("dimensions"))
        _optional_line(lines, "Materials", entity.get("materials"))
        _optional_line(lines, "Colors", entity.get("colors"))
        _optional_line(lines, "Finish", entity.get("finish"))
        _optional_line(lines, "Condition", entity.get("condition"))
        _optional_line(lines, "Placement", entity.get("placement"))
        _optional_line(lines, "Pose", entity.get("pose"))

        features = entity.get("features") if isinstance(entity.get("features"), list) else []
        if not features:
            lines.append("- Features: none")
            continue

        lines.append("")
        lines.append("Features:")
        lines.append("")
        lines.append("| ID | Feature | Surface | Visibility | Cue | Action | Note |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for feature in features:
            if not isinstance(feature, dict):
                continue
            feature_id = feature.get("id", "?")
            key = (entity_id, feature_id)
            feature_lookup[key] = feature
            entry = vis_map.get(key, {})
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(feature_id),
                        _cell(feature.get("name")),
                        _cell(feature.get("surface")),
                        _cell(entry.get("state", "untracked")),
                        _cell(entry.get("cue", "-")),
                        _cell(entry.get("prompt_action", "-")),
                        _cell(entry.get("note", "")),
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Visibility Summary"])
    groups: dict[str, list[str]] = {
        "visible": [],
        "partial": [],
        "hidden": [],
        "off_frame": [],
    }
    for entry in visibility:
        if not isinstance(entry, dict):
            continue
        key = (entry.get("entity_id"), entry.get("feature_id"))
        feature = feature_lookup.get(key)
        label = f"{key[1]} ({_feature_name(feature)})"
        state_name = entry.get("state")
        if state_name in groups:
            groups[state_name].append(label)
    labels = {
        "visible": "Visible",
        "partial": "Partial",
        "hidden": "Hidden",
        "off_frame": "Off-frame",
    }
    for state_name in ("visible", "partial", "hidden", "off_frame"):
        items = groups[state_name]
        if items:
            lines.append(f"- {labels[state_name]}: " + ", ".join(items))
    if not any(groups.values()):
        lines.append("- none")

    environment = state.get("environment") if isinstance(state.get("environment"), dict) else {}
    lines.extend(["", "## Environment"])
    for key, label in (
        ("location", "Location"),
        ("time", "Time"),
        ("weather", "Weather"),
        ("atmosphere", "Atmosphere"),
        ("absent", "Absent"),
    ):
        _optional_line(lines, label, environment.get(key))

    lighting = state.get("lighting") if isinstance(state.get("lighting"), dict) else {}
    lines.extend(["", "## Lighting"])
    for key, label in (
        ("key", "Key"),
        ("fill", "Fill"),
        ("rim", "Rim"),
        ("time_of_day", "Time of day"),
        ("color_temperature", "Color temperature"),
        ("shadows", "Shadows"),
    ):
        _optional_line(lines, label, lighting.get(key))

    color_finish = state.get("color_finish") if isinstance(state.get("color_finish"), dict) else {}
    lines.extend(["", "## Color And Finish"])
    for key, label in (
        ("palette", "Palette"),
        ("saturation", "Saturation"),
        ("contrast", "Contrast"),
        ("medium", "Medium"),
        ("grain", "Grain"),
    ):
        _optional_line(lines, label, color_finish.get(key))

    constraints = state.get("constraints") if isinstance(state.get("constraints"), dict) else {}
    lines.extend(["", "## Constraints"])
    constraint_keys = ("must_include", "must_avoid", "exact_text")
    if not any(constraints.get(key) for key in constraint_keys):
        lines.append("- none")
    for key, label in (
        ("must_include", "Must include"),
        ("must_avoid", "Must avoid"),
        ("exact_text", "Exact text"),
    ):
        _optional_line(lines, label, constraints.get(key))

    assumptions = state.get("assumptions") if isinstance(state.get("assumptions"), list) else []
    lines.extend(["", "## Assumptions"])
    if assumptions:
        for item in assumptions:
            if isinstance(item, dict):
                claim = _compact(item.get("claim"))
                reason = _compact(item.get("reason"))
                lines.append(f"- {claim} ({reason})")
            else:
                lines.append(f"- {_compact(item)}")
    else:
        lines.append("- none")

    conflicts = state.get("conflicts") if isinstance(state.get("conflicts"), list) else []
    lines.extend(["", "## Conflicts"])
    if conflicts:
        for item in conflicts:
            if not isinstance(item, dict):
                continue
            status = _compact(item.get("status"))
            claim = _compact(item.get("claim"))
            resolution = _compact(item.get("resolution"))
            lines.append(f"- [{status}] {claim} -> {resolution}")
    else:
        lines.append("- none")

    ignored = state.get("ignored") if isinstance(state.get("ignored"), list) else []
    lines.extend(["", "## Ignored"])
    if ignored:
        for item in ignored:
            if isinstance(item, dict):
                lines.append(f"- {_compact(item.get('info'))} ({_compact(item.get('reason'))})")
            else:
                lines.append(f"- {_compact(item)}")
    else:
        lines.append("- none")

    if warnings:
        lines.extend(["", "## Validation Warnings"])
        lines.extend(f"- {warning}" for warning in warnings)

    return "\n".join(lines).rstrip() + "\n"


def _entity_map(state: dict) -> dict[str, dict]:
    entities = state.get("entities") if isinstance(state.get("entities"), list) else []
    return {
        entity.get("id"): entity
        for entity in entities
        if isinstance(entity, dict) and entity.get("id")
    }


def _feature_map(entity: dict | None) -> dict[str, dict]:
    if not isinstance(entity, dict):
        return {}
    features = entity.get("features") if isinstance(entity.get("features"), list) else []
    return {
        feature.get("id"): feature
        for feature in features
        if isinstance(feature, dict) and feature.get("id")
    }


def _visibility_map(state: dict) -> dict[tuple[str, str], dict]:
    entries = state.get("visibility") if isinstance(state.get("visibility"), list) else []
    return {
        (entry.get("entity_id"), entry.get("feature_id")): entry
        for entry in entries
        if isinstance(entry, dict)
    }


def _feature_label(
    entity_id: str,
    feature_id: str,
    old_entities: dict[str, dict],
    new_entities: dict[str, dict],
) -> str:
    entity = new_entities.get(entity_id) or old_entities.get(entity_id) or {}
    feature = _feature_map(entity).get(feature_id)
    return f"{entity_id}/{feature_id} ({_feature_name(feature)})"


def build_diff(old: dict, new: dict) -> str:
    lines = [
        "# State Diff",
        f"Old: {old.get('slug', '?')} / {old.get('camera', {}).get('view_id', '?') if isinstance(old.get('camera'), dict) else '?'}",
        f"New: {new.get('slug', '?')} / {new.get('camera', {}).get('view_id', '?') if isinstance(new.get('camera'), dict) else '?'}",
        "",
    ]
    changed = False

    if old.get("visual_thesis") != new.get("visual_thesis"):
        lines.append("## Thesis")
        lines.append(f"- {_compact(old.get('visual_thesis'))} -> {_compact(new.get('visual_thesis'))}")
        lines.append("")
        changed = True

    if old.get("style") != new.get("style"):
        lines.append("## Style")
        lines.append(f"- {_compact(old.get('style'))} -> {_compact(new.get('style'))}")
        lines.append("")
        changed = True

    if old.get("platform") != new.get("platform"):
        lines.append("## Platform")
        lines.append(f"- {_compact(old.get('platform'))} -> {_compact(new.get('platform'))}")
        lines.append("")
        changed = True

    if old.get("scale_anchors") != new.get("scale_anchors"):
        lines.append("## Scale Anchors")
        lines.append(
            f"- {_compact(old.get('scale_anchors'))} -> {_compact(new.get('scale_anchors'))}"
        )
        lines.append("")
        changed = True

    old_camera = old.get("camera") if isinstance(old.get("camera"), dict) else {}
    new_camera = new.get("camera") if isinstance(new.get("camera"), dict) else {}
    camera_lines = []
    for key in (
        "view_id",
        "height",
        "distance",
        "azimuth_deg",
        "elevation_deg",
        "lens",
        "shot_scale",
        "framing",
        "focus",
        "depth_of_field",
        "aspect_ratio",
    ):
        if old_camera.get(key) != new_camera.get(key):
            camera_lines.append(
                f"- {key}: {_compact(old_camera.get(key))} -> {_compact(new_camera.get(key))}"
            )
    if camera_lines:
        lines.append("## Camera")
        lines.extend(camera_lines)
        lines.append("")
        changed = True

    old_entities = _entity_map(old)
    new_entities = _entity_map(new)
    entity_lines = []
    for entity_id in sorted(set(new_entities) - set(old_entities)):
        entity_lines.append(
            f"- added: {entity_id} ({_compact(new_entities[entity_id].get('name'))})"
        )
    for entity_id in sorted(set(old_entities) - set(new_entities)):
        entity_lines.append(
            f"- removed: {entity_id} ({_compact(old_entities[entity_id].get('name'))})"
        )
    for entity_id in sorted(set(old_entities) & set(new_entities)):
        old_entity = old_entities[entity_id]
        new_entity = new_entities[entity_id]
        for key in (
            "name",
            "role",
            "origin",
            "geometry",
            "dimensions",
            "materials",
            "colors",
            "finish",
            "condition",
            "placement",
            "pose",
        ):
            if old_entity.get(key) != new_entity.get(key):
                entity_lines.append(
                    f"- {entity_id} {key}: {_compact(old_entity.get(key))} -> {_compact(new_entity.get(key))}"
                )
        old_features = _feature_map(old_entity)
        new_features = _feature_map(new_entity)
        for feature_id in sorted(set(new_features) - set(old_features)):
            entity_lines.append(
                f"- {entity_id} feature added: {feature_id} ({_feature_name(new_features[feature_id])})"
            )
        for feature_id in sorted(set(old_features) - set(new_features)):
            entity_lines.append(
                f"- {entity_id} feature removed: {feature_id} ({_feature_name(old_features[feature_id])})"
            )
        for feature_id in sorted(set(old_features) & set(new_features)):
            old_feature = old_features[feature_id]
            new_feature = new_features[feature_id]
            for key in ("name", "surface", "description", "origin"):
                if old_feature.get(key) != new_feature.get(key):
                    entity_lines.append(
                        f"- {entity_id}/{feature_id} {key}: "
                        f"{_compact(old_feature.get(key))} -> {_compact(new_feature.get(key))}"
                    )
    if entity_lines:
        lines.append("## Entities")
        lines.extend(entity_lines)
        lines.append("")
        changed = True

    old_vis = _visibility_map(old)
    new_vis = _visibility_map(new)
    vis_lines = []
    for key in sorted(set(new_vis) - set(old_vis)):
        entry = new_vis[key]
        vis_lines.append(
            f"- added: {_feature_label(key[0], key[1], old_entities, new_entities)} "
            f"= {_compact(entry.get('state'))}/{_compact(entry.get('prompt_action'))}"
        )
    for key in sorted(set(old_vis) - set(new_vis)):
        entry = old_vis[key]
        vis_lines.append(
            f"- removed: {_feature_label(key[0], key[1], old_entities, new_entities)} "
            f"was {_compact(entry.get('state'))}/{_compact(entry.get('prompt_action'))}"
        )
    for key in sorted(set(old_vis) & set(new_vis)):
        old_entry = old_vis[key]
        new_entry = new_vis[key]
        for field in ("surface", "state", "cue", "prompt_action", "note"):
            if old_entry.get(field) != new_entry.get(field):
                vis_lines.append(
                    f"- {_feature_label(key[0], key[1], old_entities, new_entities)} "
                    f"{field}: {_compact(old_entry.get(field))} -> {_compact(new_entry.get(field))}"
                )
    if vis_lines:
        lines.append("## Visibility")
        lines.extend(vis_lines)
        lines.append("")
        changed = True

    for section, key in (
        ("Environment", "environment"),
        ("Lighting", "lighting"),
        ("Color And Finish", "color_finish"),
    ):
        old_value = old.get(key) if isinstance(old.get(key), dict) else {}
        new_value = new.get(key) if isinstance(new.get(key), dict) else {}
        section_lines = []
        for field in sorted(set(old_value) | set(new_value)):
            if old_value.get(field) != new_value.get(field):
                section_lines.append(
                    f"- {field}: {_compact(old_value.get(field))} -> {_compact(new_value.get(field))}"
                )
        if section_lines:
            lines.append(f"## {section}")
            lines.extend(section_lines)
            lines.append("")
            changed = True

    old_constraints = old.get("constraints") if isinstance(old.get("constraints"), dict) else {}
    new_constraints = new.get("constraints") if isinstance(new.get("constraints"), dict) else {}
    constraint_lines = []
    for key in ("must_include", "must_avoid", "exact_text"):
        old_items = set(old_constraints.get(key) or [])
        new_items = set(new_constraints.get(key) or [])
        for item in sorted(new_items - old_items):
            constraint_lines.append(f"- {key} added: {_compact(item)}")
        for item in sorted(old_items - new_items):
            constraint_lines.append(f"- {key} removed: {_compact(item)}")
    if constraint_lines:
        lines.append("## Constraints")
        lines.extend(constraint_lines)
        lines.append("")
        changed = True

    def note_key(item) -> str:
        if isinstance(item, str):
            return item
        return json.dumps(item, ensure_ascii=False, sort_keys=True)

    for section, key in (("Assumptions", "assumptions"), ("Ignored", "ignored")):
        old_items = old.get(key) if isinstance(old.get(key), list) else []
        new_items = new.get(key) if isinstance(new.get(key), list) else []
        old_map = {note_key(item): item for item in old_items}
        new_map = {note_key(item): item for item in new_items}
        section_lines = []
        for item_key in sorted(set(new_map) - set(old_map)):
            section_lines.append(f"- added: {_compact(new_map[item_key])}")
        for item_key in sorted(set(old_map) - set(new_map)):
            section_lines.append(f"- removed: {_compact(old_map[item_key])}")
        if section_lines:
            lines.append(f"## {section}")
            lines.extend(section_lines)
            lines.append("")
            changed = True

    old_conflicts = old.get("conflicts") if isinstance(old.get("conflicts"), list) else []
    new_conflicts = new.get("conflicts") if isinstance(new.get("conflicts"), list) else []
    old_by_claim = {
        item.get("claim"): item
        for item in old_conflicts
        if isinstance(item, dict) and item.get("claim")
    }
    new_by_claim = {
        item.get("claim"): item
        for item in new_conflicts
        if isinstance(item, dict) and item.get("claim")
    }
    conflict_lines = []
    for claim in sorted(set(new_by_claim) - set(old_by_claim)):
        conflict_lines.append(f"- added: {claim}")
    for claim in sorted(set(old_by_claim) - set(new_by_claim)):
        conflict_lines.append(f"- removed: {claim}")
    for claim in sorted(set(old_by_claim) & set(new_by_claim)):
        old_conflict = old_by_claim[claim]
        new_conflict = new_by_claim[claim]
        if old_conflict.get("status") != new_conflict.get("status"):
            conflict_lines.append(
                f"- {claim}: status {_compact(old_conflict.get('status'))} -> "
                f"{_compact(new_conflict.get('status'))}"
            )
        if old_conflict.get("resolution") != new_conflict.get("resolution"):
            conflict_lines.append(
                f"- {claim}: resolution {_compact(old_conflict.get('resolution'))} -> "
                f"{_compact(new_conflict.get('resolution'))}"
            )
    if conflict_lines:
        lines.append("## Conflicts")
        lines.extend(conflict_lines)
        lines.append("")
        changed = True

    if not changed:
        lines.append("No material changes.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def split_negative(text: str) -> tuple[str, str]:
    lower = text.lower()
    marker = None
    for candidate in ("negative prompt:", "negative:"):
        index = lower.find(candidate)
        if index != -1 and (marker is None or index < marker[0]):
            marker = (index, candidate)

    if marker is not None:
        index, candidate = marker
        visible = text[:index]
        negative = text[index + len(candidate) :]
    else:
        match = re.search(r"\s--no\s+", text)
        if match:
            visible = text[: match.start()]
            negative = text[match.end() :]
        else:
            visible = text
            negative = ""

    visible = re.sub(r"^\s*positive:\s*", "", visible, flags=re.IGNORECASE)
    return visible.strip(), negative.strip()


def name_appears_visible(text: str, name: str) -> bool:
    pattern = re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        prefix = text[max(0, match.start() - 48) : match.start()]
        if NEGATION_RE.search(prefix):
            continue
        return True
    return False


def cmd_init(args: argparse.Namespace) -> int:
    if not SLUG_RE.match(args.slug):
        raise StateError("slug must use lowercase letters, digits, and single hyphens")
    if not TEMPLATE.exists():
        raise StateError(f"template not found: {TEMPLATE}")

    out = Path(args.out)
    if out.exists() and not args.force:
        raise StateError(f"{out} already exists; pass --force to overwrite")

    try:
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(f"cannot read template: {exc}") from exc

    data["schema_version"] = SCHEMA_VERSION
    data["world_id"] = args.slug
    data["slug"] = args.slug
    data["updated"] = date.today().isoformat()
    data["mode"] = args.mode
    data["platform"] = args.platform
    data["camera"]["view_id"] = args.view
    if args.thesis:
        data["visual_thesis"] = args.thesis
    if args.subject and isinstance(data.get("entities"), list) and data["entities"]:
        data["entities"][0]["name"] = args.subject
    if args.azimuth is not None:
        data["camera"]["azimuth_deg"] = args.azimuth
    if args.elevation is not None:
        data["camera"]["elevation_deg"] = args.elevation

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise StateError(f"cannot write {out}: {exc}") from exc

    errors, warnings = validate_state(data)
    print(f"Created {out}")
    if errors:
        print("The scaffold has validation errors; check the template.")
        for error in errors:
            print(f"- {error}")
    else:
        print("State is structurally valid. Replace the placeholder values before prompting.")
    for warning in warnings:
        print(f"- warning: {warning}")
    return 0 if not errors else 1


def cmd_validate(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    errors, warnings = validate_state(state)
    summary = state_summary(state)
    if errors:
        print(f"FAIL: {args.state} ({summary})")
        print("Errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"OK: {args.state} ({summary})")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 1 if errors else 0


def cmd_brief(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    errors, warnings = validate_state(state)
    if errors:
        print(f"Cannot render brief: {len(errors)} validation error(s).", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    text = build_brief(state, warnings)
    if args.out:
        out = Path(args.out)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        except OSError as exc:
            raise StateError(f"cannot write {out}: {exc}") from exc
        print(f"Wrote {out}")
    else:
        print(text, end="")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    old = load_json(Path(args.old))
    new = load_json(Path(args.new))
    failed = False
    for label, state in (("old", old), ("new", new)):
        errors, _ = validate_state(state)
        if errors:
            failed = True
            print(f"{label} state is invalid:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
    if failed:
        return 1

    text = build_diff(old, new)
    if args.out:
        out = Path(args.out)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        except OSError as exc:
            raise StateError(f"cannot write {out}: {exc}") from exc
        print(f"Wrote {out}")
    else:
        print(text, end="")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    errors, warnings = validate_state(state)
    if errors:
        if args.json:
            print(
                json.dumps(
                    {
                        "result": "fail",
                        "state": args.state,
                        "errors": [f"state validation: {error}" for error in errors],
                        "warnings": warnings,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"State validation failed for {args.state}:")
            for error in errors:
                print(f"- {error}")
        return 1

    if args.text is not None:
        prompt = args.text
    elif args.file:
        try:
            prompt = Path(args.file).read_text(encoding="utf-8")
        except OSError as exc:
            raise StateError(f"cannot read prompt file {args.file}: {exc}") from exc
    else:
        prompt = sys.stdin.read()

    prompt = prompt.strip()
    if not prompt:
        raise StateError("prompt is empty")

    platform = (args.platform or state.get("platform") or "portable").strip().lower()
    visible, negative = split_negative(prompt)
    full_text = prompt.lower()

    check_errors: list[str] = []
    check_warnings: list[str] = list(warnings)

    if not has_any(prompt, CAMERA_PATTERNS):
        check_warnings.append(
            "prompt has no explicit camera control; add height, angle, lens, or framing"
        )
    if not has_any(prompt, LIGHT_PATTERNS):
        check_warnings.append(
            "prompt has no explicit lighting control; add source direction or quality"
        )
    if not has_any(prompt, COMPOSITION_PATTERNS):
        check_warnings.append(
            "prompt has no explicit composition control; add placement, crop, or occupancy"
        )
    if platform in STABLE_DIFFUSION_PLATFORMS and not (
        "positive:" in full_text and "negative:" in full_text
    ):
        check_warnings.append(
            "stable-diffusion-style output should use Positive: and Negative: blocks"
        )

    for term in STATE_TERMS:
        if term in full_text:
            check_warnings.append(f"prompt contains state terminology: {term!r}")
            break

    entities = _entity_map(state)
    visibility = state.get("visibility") if isinstance(state.get("visibility"), list) else []
    hidden_checked = 0
    for entry in visibility:
        if not isinstance(entry, dict):
            continue
        if entry.get("state") not in {"hidden", "off_frame"}:
            continue
        if entry.get("prompt_action") not in {"omit", "negative"}:
            continue
        feature = _feature_map(entities.get(entry.get("entity_id"))).get(entry.get("feature_id"))
        name = feature.get("name") if isinstance(feature, dict) else None
        if not isinstance(name, str) or len(name.strip()) < 4:
            continue
        if name.strip().lower() in GENERIC_FEATURE_NAMES:
            continue
        hidden_checked += 1
        if name_appears_visible(visible, name.strip()):
            check_errors.append(
                f'hidden feature "{name.strip()}" appears in the visible prompt; '
                "remove it or move it to the negative prompt"
            )

    result = "fail" if check_errors else "pass"
    if args.json:
        print(
            json.dumps(
                {
                    "result": result,
                    "state": args.state,
                    "platform": platform,
                    "hidden_features_checked": hidden_checked,
                    "errors": check_errors,
                    "warnings": check_warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Result: {result.upper()}")
        print(f"State: {args.state}")
        print(f"Platform: {platform}")
        print(f"Hidden features checked: {hidden_checked}")
        if check_errors:
            print("Errors:")
            for error in check_errors:
                print(f"- {error}")
        if check_warnings:
            print("Warnings:")
            for warning in check_warnings:
                print(f"- {warning}")
        if not check_errors and not check_warnings:
            print("No issues found.")

    return 1 if check_errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage dump-info image reconstruction states."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a state from the bundled template.")
    init_parser.add_argument("--out", required=True, help="Output state JSON path.")
    init_parser.add_argument("--slug", required=True, help="Project slug, lowercase-hyphenated.")
    init_parser.add_argument("--mode", choices=sorted(MODES), default="object")
    init_parser.add_argument("--platform", default="portable")
    init_parser.add_argument("--view", default="front-three-quarter", help="Camera view id label.")
    init_parser.add_argument("--azimuth", type=float, help="Camera azimuth in degrees.")
    init_parser.add_argument("--elevation", type=float, help="Camera elevation in degrees.")
    init_parser.add_argument("--subject", help="Set the primary entity name.")
    init_parser.add_argument("--thesis", help="Set the visual thesis.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite an existing file.")
    init_parser.set_defaults(func=cmd_init)

    validate_parser = subparsers.add_parser("validate", help="Validate a state JSON file.")
    validate_parser.add_argument("state")
    validate_parser.set_defaults(func=cmd_validate)

    brief_parser = subparsers.add_parser("brief", help="Render a reconstruction brief.")
    brief_parser.add_argument("state")
    brief_parser.add_argument("--out", help="Write the brief to a file instead of stdout.")
    brief_parser.set_defaults(func=cmd_brief)

    diff_parser = subparsers.add_parser("diff", help="Compare two state files.")
    diff_parser.add_argument("old")
    diff_parser.add_argument("new")
    diff_parser.add_argument("--out", help="Write the diff to a file instead of stdout.")
    diff_parser.set_defaults(func=cmd_diff)

    check_parser = subparsers.add_parser(
        "check", help="Check a prompt for hidden-feature leaks and missing controls."
    )
    check_parser.add_argument("--state", required=True, help="State JSON file.")
    prompt_group = check_parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--file", help="Prompt text file.")
    prompt_group.add_argument("--text", help="Prompt text.")
    check_parser.add_argument("--platform", help="Override the state platform.")
    check_parser.add_argument("--json", action="store_true", help="Emit a JSON report.")
    check_parser.set_defaults(func=cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except StateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
