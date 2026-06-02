from scraper.models import TwitterUser, Tweet


def _get(d: dict, *keys, default=None):
    for key in keys:
        if "/" in key:
            parts = key.split("/")
            val = d
            for p in parts:
                if isinstance(val, dict):
                    val = val.get(p)
                else:
                    val = None
                    break
            if val is not None:
                return val
        else:
            if key in d and d[key] is not None:
                return d[key]
    return default


def parse_user(raw: dict) -> TwitterUser:
    return TwitterUser(
        name=_get(raw, "displayName", "name", "full_name", default=""),
        username=_get(raw, "username", "screen_name", default=""),
        avatar=_get(raw, "avatar", "profile_image_url_https",
                     "profilePicture", "profile_image_url", default=""),
        bio=_get(raw, "bio", "description", "biography", default=""),
        location=_get(raw, "location", "userLocation", default=""),
        followers=_get(raw, "followers", "followers_count", "followersCount", default=0),
        following=_get(raw, "following", "friends_count", "friendsCount", default=0),
        tweets_count=_get(raw, "tweets", "statuses_count", "tweetCount", default=0),
        verified=_get(raw, "verified", "is_verified", "isBlueVerified",
                       "is_blue_verified", default=False),
        joined=_get(raw, "joined", "created_at", "joinDate", default=""),
        profile_banner=_get(raw, "banner", "profile_banner_url", "bannerUrl", default=""),
        raw=raw,
    )


def parse_tweets(raw: dict | list) -> list[Tweet]:
    if isinstance(raw, dict):
        raw = _get(raw, "tweets", "data", default=raw)
        if isinstance(raw, dict):
            raw = list(raw.values())
    if not isinstance(raw, list):
        return []

    tweets = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        stats = _get(item, "stats", default={}) or {}
        tweets.append(Tweet(
            id=str(_get(item, "id", "id_str", "tweetId", default="")),
            text=_get(item, "content", "text", "full_text", default=""),
            created_at=_get(item, "createdAt", "created_at", "timestamp",
                            "tweet_created_at", default=""),
            likes=_get(stats, "likes", "likeCount", "favorite_count",
                       "favouritesCount", default=0),
            retweets=_get(stats, "retweets", "retweetCount", "retweet_count", default=0),
            replies=_get(stats, "replies", "replyCount", "reply_count", default=0),
            views=_get(stats, "views", "viewCount", "views_count", default=0),
            quote_count=_get(stats, "quotes", "quoteCount", "quote_count", default=0),
            is_retweet=_get(item, "isRetweet", "is_retweet", "retweeted", default=False),
            author_username=_get(item, "author/username", "author/screen_name",
                                 "author/userName", "userName", default=""),
            raw=item,
        ))
    return tweets
