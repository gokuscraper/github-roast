import json
from pathlib import Path
from typing import Optional

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"


def _user_dir(username: str) -> Path:
    return DATA_ROOT / username.lower()


def save_raw(username: str, user_raw: dict, repos_raw: list, events_raw: list):
    udir = _user_dir(username)
    udir.mkdir(parents=True, exist_ok=True)

    with open(udir / "user.json", "w", encoding="utf-8") as f:
        json.dump(user_raw, f, ensure_ascii=False, indent=2)
    with open(udir / "repos.json", "w", encoding="utf-8") as f:
        json.dump(repos_raw, f, ensure_ascii=False, indent=2)
    with open(udir / "events.json", "w", encoding="utf-8") as f:
        json.dump(events_raw, f, ensure_ascii=False, indent=2)


def load_raw(username: str) -> tuple[Optional[dict], Optional[list], Optional[list]]:
    udir = _user_dir(username)
    user_raw = None
    repos_raw = None
    events_raw = None

    user_path = udir / "user.json"
    repos_path = udir / "repos.json"
    events_path = udir / "events.json"

    if user_path.exists():
        with open(user_path, "r", encoding="utf-8") as f:
            user_raw = json.load(f)
    if repos_path.exists():
        with open(repos_path, "r", encoding="utf-8") as f:
            repos_raw = json.load(f)
    if events_path.exists():
        with open(events_path, "r", encoding="utf-8") as f:
            events_raw = json.load(f)

    return user_raw, repos_raw, events_raw


def has_cached(username: str) -> bool:
    udir = _user_dir(username)
    return (udir / "user.json").exists()
