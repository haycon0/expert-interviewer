"""The model catalog (models.json) and checks for whether each model is set up.

A model is written "provider:model-name" (e.g. "anthropic:claude-haiku-5-5"), or
"demo" for canned answers. A model is ready when its provider's package is
installed, its API key is in .env, and, for Ollama, the app is running and the
model has been downloaded.
"""

import importlib.util
import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
CATALOG_FILE = ROOT / "models.json"
ENV_FILE = ROOT / ".env"
REQUIREMENTS_FILE = ROOT / "requirements.txt"

DEMO = "demo"
DEFAULT_MODEL = "anthropic:claude-sonnet-5-5"

# Agents whose model can be chosen, and their optional .env override.
AGENTS = {
    "witness": "MODEL_WITNESS",
    "checker": "MODEL_CHECKER",
    "criteria": "MODEL_CRITERIA",
    "grader": "MODEL_GRADER",
}

# Rough token use of a typical 15-25 question interview, for the cost estimate.
EST_INPUT_MTOK, EST_OUTPUT_MTOK = 0.15, 0.04


def load_catalog() -> dict:
    return json.loads(CATALOG_FILE.read_text(encoding="utf-8"))


def reload_env() -> None:
    """Re-read .env so a key saved while the app is running takes effect without a restart."""
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=True)


def forced_demo() -> bool:
    return os.getenv("MOCK_LLM") == "1"


def default_models() -> dict:
    """Models from .env (MODEL plus per-agent overrides), used to pre-select the picker."""
    main = os.getenv("MODEL", "").strip() or DEFAULT_MODEL
    return {agent: os.getenv(var, "").strip() or main for agent, var in AGENTS.items()}


def _ollama_models() -> set[str] | None:
    """Names of downloaded Ollama models, or None if Ollama isn't running."""
    import urllib.request

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    if not host.startswith("http"):
        host = "http://" + host
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=1.5) as r:
            tags = json.loads(r.read())
    except Exception:
        return None
    names = set()
    for m in tags.get("models", []):
        names.add(m["name"])
        if m["name"].endswith(":latest"):
            names.add(m["name"][: -len(":latest")])
    return names


def _requirement_state(pip_name: str) -> str:
    """'listed', 'commented' (present but switched off with #), or 'absent' in requirements.txt."""
    import re

    def name_of(line: str) -> str:  # "langchain-openai==1.7.4" -> "langchain-openai"
        return re.split(r"[=<>!~\[;\s]", line.strip(), maxsplit=1)[0].lower()

    try:
        lines = [l.strip() for l in REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines()]
    except OSError:
        return "absent"
    pip_name = pip_name.lower()
    if any(not l.startswith("#") and name_of(l) == pip_name for l in lines):
        return "listed"
    if any(l.startswith("#") and name_of(l.lstrip("#")) == pip_name for l in lines):
        return "commented"
    return "absent"


def model_status(model_id: str, catalog: dict, ollama: set[str] | None | bool = False) -> dict:
    """Whether a model is ready, and if not, each problem to fix.

    Pass `ollama` (from _ollama_models) when checking many models, to query Ollama once.
    """
    if model_id == DEMO or forced_demo():
        return {"ready": True, "problems": []}
    provider_id, _, name = model_id.partition(":")
    provider = catalog["providers"].get(provider_id)
    if not provider or not name:
        return {"ready": False, "problems": [{"type": "unknown", "provider": provider_id}]}

    problems = []
    if importlib.util.find_spec(provider["package"]) is None:
        problems.append({"type": "package", "pip": provider["pip"],
                         "requirement": _requirement_state(provider["pip"])})
    if provider.get("local"):
        tags = _ollama_models() if ollama is False else ollama
        if tags is None:
            problems.append({"type": "ollama_not_running"})
        elif name not in tags:
            problems.append({"type": "ollama_model_missing", "name": name})
    elif not os.getenv(provider["key_env"], "").strip():
        problems.append({"type": "key", "key_env": provider["key_env"]})
    return {"ready": not problems, "problems": problems}


def estimate(price: list | None) -> float | None:
    if not price:
        return None
    return round(price[0] * EST_INPUT_MTOK + price[1] * EST_OUTPUT_MTOK, 2)


def catalog_with_status() -> dict:
    """The catalog for the setup page: every model with its readiness and cost estimate."""
    reload_env()
    catalog = load_catalog()
    ollama = _ollama_models()
    models = []
    for m in catalog["models"]:
        models.append({**m, "provider": m["id"].partition(":")[0] if m["id"] != DEMO else DEMO,
                       "estimate": estimate(m.get("price")),
                       "status": model_status(m["id"], catalog, ollama)})
    return {
        "checked": catalog.get("checked"),
        "tiers": catalog["tiers"],
        "providers": catalog["providers"],
        "models": models,
        "defaults": {a: DEMO for a in AGENTS} if forced_demo() else default_models(),
        "forced_demo": forced_demo(),
        # Present only in a restricted edition (the online branch): a notice for the
        # setup page and whether models outside the list may be typed in.
        "edition": catalog.get("edition"),
    }


def describe_problems(model_id: str, status: dict, catalog: dict) -> str:
    """A one-line, plain-English summary of what's missing (for API error messages)."""
    provider = catalog["providers"].get(model_id.partition(":")[0], {})
    name = provider.get("name", model_id)
    parts = []
    for p in status["problems"]:
        if p["type"] == "unknown":
            parts.append(f"'{model_id}' isn't a recognized model (expected provider:model-name)")
        elif p["type"] == "package":
            parts.append(f"the {name} package ({p['pip']}) isn't installed")
        elif p["type"] == "key":
            parts.append(f"{p['key_env']} isn't set in .env")
        elif p["type"] == "ollama_not_running":
            parts.append("Ollama isn't running")
        elif p["type"] == "ollama_model_missing":
            parts.append(f"the Ollama model '{p['name']}' hasn't been downloaded")
    return f"{model_id} isn't set up: " + "; ".join(parts) + ". See docs/MODELS.md."
