from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TwitterUser:
    name: str
    username: str
    avatar: str
    bio: str
    location: str
    followers: int
    following: int
    tweets_count: int
    verified: bool
    joined: str
    profile_banner: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class Tweet:
    id: str
    text: str
    created_at: str
    likes: int
    retweets: int
    replies: int
    views: int
    quote_count: int = 0
    is_retweet: bool = False
    author_username: str = ""
    raw: dict = field(default_factory=dict)
