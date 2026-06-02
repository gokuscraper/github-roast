from scraper.models import Tweet


def format_tweets_md(tweets: list[Tweet]) -> str:
    """格式化推文为 Markdown（和 Wordware route.ts 格式一致）。"""
    parts = []
    for t in tweets:
        prefix = "RT " if t.is_retweet else ""
        text_indented = "\n> ".join(t.text.split("\n"))
        parts.append(
            f"**{prefix}@{t.author_username} - {t.created_at}**\n\n"
            f"> {text_indented}\n\n"
            f"*retweets: {t.retweets}, replies: {t.replies}, "
            f"likes: {t.likes}, views: {t.views}*"
        )
    return "\n---\n\n".join(parts)


def summarize_tweets(tweets: list[Tweet]) -> dict:
    """返回推文统计摘要。"""
    if not tweets:
        return {"count": 0}
    likes = [t.likes for t in tweets]
    views = [t.views for t in tweets]
    return {
        "count": len(tweets),
        "avg_likes": round(sum(likes) / len(likes)),
        "max_likes": max(likes),
        "avg_views": round(sum(views) / len(views)),
        "max_views": max(views),
        "total_retweets": sum(t.retweets for t in tweets),
    }
