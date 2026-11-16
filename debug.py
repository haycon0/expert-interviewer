"""Debugging mode: an example case filled in for you, a chosen witness persona and
variations, a scripted interview to start from, and an optional skip of the document check.

It lives on its own page, /debug (linked from the setup page on your own computer).
It's unavailable when the app runs online (access.online()), so
it can't be used to see or steer hidden parts of an interview on a published site.

Example cases live in debug/cases/*.json (witness, role, background, documents);
scripts in debug/scripts/*.json add a transcript to start from.
"""

import json
from pathlib import Path

import access

ROOT = Path(__file__).parent
CASES_DIR = ROOT / "debug" / "cases"
SCRIPTS_DIR = ROOT / "debug" / "scripts"


def available() -> bool:
    """Debugging mode can be used: always on your own computer, never online."""
    return not access.online()


def _files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.json")) if folder.exists() else []


def _inside_project(rel: str) -> Path:
    """Resolve a path from a case or script, refusing anything outside the project folder."""
    p = (ROOT / rel).resolve()
    if ROOT.resolve() not in p.parents:
        raise ValueError(f"File path {rel!r} is outside the project folder.")
    return p


def _background(item: dict) -> str:
    if item.get("case_background"):
        return item["case_background"]
    if item.get("case_background_file"):
        return _inside_project(item["case_background_file"]).read_text(encoding="utf-8").strip()
    return ""


def _summary(p: Path) -> dict:
    s = json.loads(p.read_text(encoding="utf-8"))
    return {"id": p.stem, "name": s.get("name", p.stem), "description": s.get("description", ""),
            "expert_name": s.get("expert_name", ""), "expert_role": s.get("expert_role", ""),
            "case_background": _background(s), "documents": [Path(d).name for d in s.get("documents", [])],
            "turns": len(s.get("transcript", [])), "resume_hint": s.get("resume_hint", ""),
            # The persona and variations a script was written for (preset in the panel).
            "persona": s.get("persona", ""), "variables": s.get("variables", ""),
            "default": bool(s.get("default"))}


def list_cases() -> list[dict]:
    return [_summary(p) for p in _files(CASES_DIR)]


def list_scripts() -> list[dict]:
    return [_summary(p) for p in _files(SCRIPTS_DIR)]


def _load(folder: Path, item_id: str, kind: str) -> dict:
    """A case or script with its documents read from disk: {..., "documents": [(name, bytes)]}."""
    path = folder / f"{Path(item_id).name}.json"
    if not path.exists():
        raise ValueError(f"No debug {kind} named {item_id!r}.")
    s = json.loads(path.read_text(encoding="utf-8"))
    s["case_background"] = _background(s)
    s["documents"] = [(Path(rel).name, _inside_project(rel).read_bytes()) for rel in s.get("documents", [])]
    return s


def load_case(case_id: str) -> dict:
    return _load(CASES_DIR, case_id, "case")


def load_script(script_id: str) -> dict:
    return _load(SCRIPTS_DIR, script_id, "script")
