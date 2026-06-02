from scraper.client import fetch_api, fetch_api_full
from scraper.config import USER_API, TWEETS_API
from scraper.models import TwitterUser, Tweet
from scraper.parser import parse_user, parse_tweets
from scraper.storage import save_raw


def fetch_user(username: str) -> TwitterUser:
    """抓取用户资料并返回 TwitterUser 对象。"""
    raw = fetch_api(USER_API.format(username=username))
    return parse_user(raw)


def fetch_tweets(username: str) -> list[Tweet]:
    """抓取用户推文并返回 Tweet 对象列表。"""
    raw = fetch_api(TWEETS_API.format(username=username))
    return parse_tweets(raw)


def fetch_all(username: str) -> tuple[TwitterUser, list[Tweet]]:
    """同时抓取用户资料和推文。"""
    return fetch_user(username), fetch_tweets(username)


def scrape_and_save(username: str) -> tuple[TwitterUser, list[Tweet]]:
    """抓取用户资料+推文，并保存原始数据到 data/{username}/。"""
    path_user = USER_API.format(username=username)
    path_tweets = TWEETS_API.format(username=username)
    user_full = fetch_api_full(path_user)
    tweets_full = fetch_api_full(path_tweets)

    user_raw = user_full.get("data", {}) if isinstance(user_full, dict) else {}
    tweets_raw = tweets_full.get("data", {}) if isinstance(tweets_full, dict) else {}

    save_raw(username, user_full, tweets_full)

    return parse_user(user_raw), parse_tweets(tweets_raw)
