import os
import time

import requests

from github_scraper.config import API_BASE, REQUEST_TIMEOUT

_session = None


def _get_token() -> str:
    try:
        import streamlit as st
        token = st.secrets.get("GITHUB_TOKEN", "")
        if token:
            return token
    except Exception:
        pass
    return os.getenv("GITHUB_TOKEN", "")


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        token = _get_token()
        if token:
            _session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        })
        _session.headers.update({
            "User-Agent": "wukong-github-analyzer/1.0",
        })
    return _session


def get(endpoint: str, params: dict | None = None) -> dict | list:
    session = _get_session()
    url = f"{API_BASE}{endpoint}"

    for attempt in range(3):
        resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)

        if resp.status_code == 403 and int(resp.headers.get("X-RateLimit-Remaining", 1)) == 0:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", 0))
            wait = max(reset_ts - time.time(), 1) + 1
            time.sleep(wait)
            continue

        if resp.status_code == 404:
            raise RuntimeError(f"GitHub user not found: {endpoint}")

        if resp.status_code == 401:
            raise RuntimeError("GitHub token is invalid or expired")

        resp.raise_for_status()
        return resp.json()

    raise RuntimeError(f"Failed to fetch {url} after 3 retries")
