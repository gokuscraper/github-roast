from scraper.subprocess_client import fetch_all, shutdown
from scraper.models import TwitterUser, Tweet

__all__ = [
    "fetch_all",
    "TwitterUser",
    "Tweet",
    "shutdown",
]


def close_browser():
    shutdown()
