from typing import Any

from github_scraper.models import GitHubUser, GitHubRepo, GitHubEvent


def parse_user(raw: dict) -> GitHubUser:
    return GitHubUser(
        login=raw.get("login", ""),
        name=raw.get("name") or "",
        avatar_url=raw.get("avatar_url", ""),
        html_url=raw.get("html_url", ""),
        bio=raw.get("bio") or "",
        company=raw.get("company") or "",
        location=raw.get("location") or "",
        blog=raw.get("blog") or "",
        twitter_username=raw.get("twitter_username") or "",
        public_repos=raw.get("public_repos", 0),
        public_gists=raw.get("public_gists", 0),
        followers=raw.get("followers", 0),
        following=raw.get("following", 0),
        created_at=raw.get("created_at", ""),
        updated_at=raw.get("updated_at", ""),
        raw=raw,
    )


def _get_license_name(raw: dict) -> str:
    lic = raw.get("license")
    if isinstance(lic, dict):
        return lic.get("spdx_id") or lic.get("name") or ""
    return ""


def parse_repos(raw: list[dict]) -> list[GitHubRepo]:
    repos = []
    for item in raw:
        repos.append(GitHubRepo(
            id=item.get("id", 0),
            name=item.get("name", ""),
            full_name=item.get("full_name", ""),
            description=item.get("description") or "",
            html_url=item.get("html_url", ""),
            language=item.get("language"),
            topics=item.get("topics", []),
            stars=item.get("stargazers_count", 0),
            forks=item.get("forks_count", 0),
            open_issues=item.get("open_issues_count", 0),
            license_name=_get_license_name(item),
            size=item.get("size", 0),
            is_fork=item.get("fork", False),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
            pushed_at=item.get("pushed_at", ""),
            raw=item,
        ))
    return repos


def parse_events(raw: list[dict]) -> list[GitHubEvent]:
    events = []
    for item in raw:
        repo = item.get("repo", {}) or {}
        actor = item.get("actor", {}) or {}
        events.append(GitHubEvent(
            id=item.get("id", ""),
            type=item.get("type", ""),
            repo_name=repo.get("name", ""),
            repo_url=repo.get("url", ""),
            actor_login=actor.get("login", ""),
            created_at=item.get("created_at", ""),
            payload=item.get("payload", {}),
        ))
    return events
