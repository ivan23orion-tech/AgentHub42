import json
from pathlib import Path

DB_PATH = Path("agenthub42.json")


def _ensure_db() -> None:
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"tasks": [], "submissions": []}, indent=2), encoding="utf-8")


def load_db() -> dict:
    _ensure_db()
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def save_db(data: dict) -> None:
    DB_PATH.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
