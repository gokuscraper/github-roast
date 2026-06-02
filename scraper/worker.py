"""
scraper/worker.py — 在独立进程中运行爬虫，通过 stdin/stdout JSON 通信。

协议：
  主进程 → stdin:  {"username": "xxx"}
  主进程 ← stdout: {"type": "log",  "message": "..."}      (进度消息)
  主进程 ← stdout: {"type": "result", "user": {...}, "tweets": [...]}  (最终结果)
  主进程 ← stdout: {"type": "error", "message": "..."}      (错误)
"""

import io
import json
import sys
from pathlib import Path

# Worker 输出必须用 UTF-8，避免 GBK 编码报错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scraper.fetcher import fetch_all, scrape_and_save
from scraper.client import shutdown
from scraper.models import TwitterUser, Tweet


def _log(msg: str):
    _send({"type": "log", "message": msg})


def _send(data: dict):
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _user_to_dict(u: TwitterUser) -> dict:
    return {
        "name": u.name,
        "username": u.username,
        "avatar": u.avatar,
        "bio": u.bio,
        "location": u.location,
        "followers": u.followers,
        "following": u.following,
        "tweets_count": u.tweets_count,
        "verified": u.verified,
        "joined": u.joined,
        "raw": u.raw,
    }


def _tweet_to_dict(t: Tweet) -> dict:
    return {
        "id": t.id,
        "text": t.text,
        "created_at": t.created_at,
        "likes": t.likes,
        "retweets": t.retweets,
        "replies": t.replies,
        "views": t.views,
        "quote_count": t.quote_count,
        "is_retweet": t.is_retweet,
        "author_username": t.author_username,
        "raw": t.raw,
    }


def main():
    line = sys.stdin.readline()
    if not line:
        return

    try:
        cmd = json.loads(line)
        username = cmd.get("username", "")
    except json.JSONDecodeError as e:
        _send({"type": "error", "message": f"Invalid command: {e}"})
        return

    if not username:
        _send({"type": "error", "message": "Missing 'username' field"})
        return

    _log(f"Launching browser...")
    _log(f"Scraping @{username}...")

    try:
        user, tweets = scrape_and_save(username)
    except Exception as e:
        try:
            shutdown()
        except Exception:
            pass
        _send({"type": "error", "message": str(e)})
        return

    _log(f"Done: {len(tweets)} tweets for @{username}")

    try:
        shutdown()
    except Exception:
        pass

    _send({
        "type": "result",
        "user": _user_to_dict(user),
        "tweets": [_tweet_to_dict(t) for t in tweets],
    })


if __name__ == "__main__":
    main()
