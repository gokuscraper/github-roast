from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GitHubUser:
    login: str
    name: str
    avatar_url: str
    html_url: str
    bio: str
    company: str
    location: str
    blog: str
    twitter_username: str
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str
    updated_at: str
    raw: dict = field(default_factory=dict)


@dataclass
class GitHubRepo:
    id: int
    name: str
    full_name: str
    description: str
    html_url: str
    language: Optional[str]
    topics: list[str]
    stars: int
    forks: int
    open_issues: int
    license_name: str
    size: int
    is_fork: bool
    created_at: str
    updated_at: str
    pushed_at: str
    raw: dict = field(default_factory=dict)


@dataclass
class GitHubEvent:
    id: str
    type: str
    repo_name: str
    repo_url: str
    actor_login: str
    created_at: str
    payload: dict = field(default_factory=dict)
