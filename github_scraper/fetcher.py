from github_scraper.client import get
from github_scraper.config import USER_API, REPOS_API, EVENTS_API, PER_PAGE_REPOS, PER_PAGE_EVENTS, SORT_REPOS, DIRECTION_REPOS
from github_scraper.models import GitHubUser, GitHubRepo, GitHubEvent
from github_scraper.parser import parse_user, parse_repos, parse_events
from github_scraper.storage import save_raw


def fetch_user(username: str) -> GitHubUser:
    raw = get(USER_API.format(username=username))
    return parse_user(raw)


def fetch_repos(username: str) -> list[GitHubRepo]:
    raw = get(REPOS_API.format(username=username), params={
        "per_page": PER_PAGE_REPOS,
        "sort": SORT_REPOS,
        "direction": DIRECTION_REPOS,
        "type": "all",
    })
    return parse_repos(raw)


def fetch_events(username: str) -> list[GitHubEvent]:
    raw = get(EVENTS_API.format(username=username), params={
        "per_page": PER_PAGE_EVENTS,
    })
    return parse_events(raw)


def fetch_all(username: str) -> tuple[GitHubUser, list[GitHubRepo], list[GitHubEvent]]:
    user_raw = get(USER_API.format(username=username))
    repos_raw = get(REPOS_API.format(username=username), params={
        "per_page": PER_PAGE_REPOS,
        "sort": SORT_REPOS,
        "direction": DIRECTION_REPOS,
        "type": "all",
    })
    events_raw = get(EVENTS_API.format(username=username), params={
        "per_page": PER_PAGE_EVENTS,
    })

    save_raw(username, user_raw, repos_raw, events_raw)

    return parse_user(user_raw), parse_repos(repos_raw), parse_events(events_raw)
