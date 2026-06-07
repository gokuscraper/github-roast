from typing import Counter

from github_scraper.models import GitHubUser, GitHubRepo, GitHubEvent


def format_data_md(user: GitHubUser, repos: list[GitHubRepo], events: list[GitHubEvent]) -> str:
    parts = []

    user_md = (
        f"**Profile**\n\n"
        f"- Name: {user.name or user.login}\n"
        f"- Login: {user.login}\n"
        f"- Bio: {user.bio or '(none)'}\n"
        f"- Company: {user.company or '(none)'}\n"
        f"- Location: {user.location or '(none)'}\n"
        f"- Blog: {user.blog or '(none)'}\n"
        f"- Twitter: {user.twitter_username or '(none)'}\n"
        f"- Followers: {user.followers}\n"
        f"- Following: {user.following}\n"
        f"- Public repos: {user.public_repos}\n"
        f"- Public gists: {user.public_gists}\n"
        f"- Joined: {user.created_at[:10] if user.created_at else '(unknown)'}"
    )
    parts.append(user_md)

    repo_parts = []
    for r in repos:
        fork_flag = " (fork)" if r.is_fork else ""
        topics_str = f" [{', '.join(r.topics[:5])}]" if r.topics else ""
        repo_parts.append(
            f"- **{r.name}**{fork_flag} — {r.description or '(no description)'}\n"
            f"  ⭐ {r.stars} | 🍴 {r.forks} | 🔤 {r.language or '?'}{topics_str}\n"
            f"  Updated: {r.pushed_at[:10] if r.pushed_at else '?'}"
        )
    parts.append(f"**Repos ({len(repos)})**\n\n" + "\n".join(repo_parts))

    if events:
        event_parts = []
        for e in events[:30]:
            event_parts.append(f"- {e.type} → {e.repo_name} ({e.created_at[:10]})")
        parts.append(f"**Recent events ({len(events)})**\n\n" + "\n".join(event_parts))

    return "\n\n---\n\n".join(parts)


def summarize_repos(repos: list[GitHubRepo], events: list[GitHubEvent], followers: int = 0) -> dict:
    total_stars = sum(r.stars for r in repos)
    languages = [r.language for r in repos if r.language]
    lang_counts = Counter(languages)
    top_langs = [{"name": k, "count": v} for k, v in lang_counts.most_common(10)]

    event_types = Counter(e.type for e in events)

    fork_count = sum(1 for r in repos if r.is_fork)
    original_count = sum(1 for r in repos if not r.is_fork)
    account_value = max(0,
        total_stars * 5 +
        followers * 10 +
        original_count * 30 -
        fork_count * 20
    )

    return {
        "repos_count": len(repos),
        "total_stars": total_stars,
        "total_forks": sum(r.forks for r in repos),
        "languages_count": len(lang_counts),
        "top_languages": top_langs,
        "events_count": len(events),
        "event_types": dict(event_types.most_common(5)),
        "fork_count": fork_count,
        "original_count": original_count,
        "account_value": account_value,
    }
