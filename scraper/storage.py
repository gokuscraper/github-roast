import json
import os
from pathlib import Path
from typing import Optional

from scraper.models import TwitterUser, Tweet

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"


def _user_dir(username: str) -> Path:
    return DATA_ROOT / username.lower()


def save_raw(username: str, user_raw: dict, tweets_raw: dict):
    """保存原始 API 响应到 data/{username}/ 目录。"""
    udir = _user_dir(username)
    udir.mkdir(parents=True, exist_ok=True)

    with open(udir / "user.json", "w", encoding="utf-8") as f:
        json.dump(user_raw, f, ensure_ascii=False, indent=2)
    with open(udir / "tweets.json", "w", encoding="utf-8") as f:
        json.dump(tweets_raw, f, ensure_ascii=False, indent=2)


def load_raw(username: str) -> tuple[Optional[dict], Optional[dict]]:
    """从磁盘加载原始 API 响应。"""
    udir = _user_dir(username)
    user_raw = None
    tweets_raw = None

    user_path = udir / "user.json"
    tweets_path = udir / "tweets.json"

    if user_path.exists():
        with open(user_path, "r", encoding="utf-8") as f:
            user_raw = json.load(f)
    if tweets_path.exists():
        with open(tweets_path, "r", encoding="utf-8") as f:
            tweets_raw = json.load(f)

    return user_raw, tweets_raw


def has_cached(username: str) -> bool:
    """检查是否有缓存的抓取数据。"""
    udir = _user_dir(username)
    return (udir / "user.json").exists() and (udir / "tweets.json").exists()
