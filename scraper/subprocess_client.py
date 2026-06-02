import json
import subprocess
import sys
from pathlib import Path
from typing import Generator

from scraper.models import TwitterUser, Tweet

_WORKER = str(Path(__file__).resolve().parent / "worker.py")


def _parse_user(d: dict) -> TwitterUser:
    return TwitterUser(
        name=d.get("name", ""),
        username=d.get("username", ""),
        avatar=d.get("avatar", ""),
        bio=d.get("bio", ""),
        location=d.get("location", ""),
        followers=d.get("followers", 0),
        following=d.get("following", 0),
        tweets_count=d.get("tweets_count", 0),
        verified=d.get("verified", False),
        joined=d.get("joined", ""),
        raw=d.get("raw", {}),
    )


def _parse_tweet(d: dict) -> Tweet:
    return Tweet(
        id=d.get("id", ""),
        text=d.get("text", ""),
        created_at=d.get("created_at", ""),
        likes=d.get("likes", 0),
        retweets=d.get("retweets", 0),
        replies=d.get("replies", 0),
        views=d.get("views", 0),
        quote_count=d.get("quote_count", 0),
        is_retweet=d.get("is_retweet", False),
        author_username=d.get("author_username", ""),
        raw=d.get("raw", {}),
    )


def fetch_all(username: str) -> tuple[TwitterUser, list[Tweet]]:
    """在子进程中运行爬虫，返回 (TwitterUser, list[Tweet])。"""
    proc = subprocess.Popen(
        [sys.executable, _WORKER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )

    cmd = json.dumps({"username": username})
    out_b, err_b = proc.communicate(input=cmd.encode("utf-8"), timeout=300)

    out = out_b.decode("utf-8", errors="replace")
    err = err_b.decode("utf-8", errors="replace")

    # 只将 stdout 无结果视为错误；stderr 可能包含 CloakBrowser banner 等非错误信息
    user = None
    tweets = []

    for line in out.strip().split("\n"):
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        t = msg.get("type")
        if t == "error":
            raise RuntimeError(msg.get("message", "Unknown error"))
        elif t == "result":
            user = _parse_user(msg.get("user", {}))
            tweets = [_parse_tweet(tw) for tw in msg.get("tweets", [])]

    if user is None:
        raise RuntimeError(f"Worker did not return a result for @{username}")

    return user, tweets


def shutdown():
    """子进程模式下 shutdown 是无操作的（进程已退出）。"""
    pass
