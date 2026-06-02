import json
import os
from openai import OpenAI

from scraper.models import TwitterUser, Tweet
from lib.tweet_utils import format_tweets_md

ANALYSIS_PROMPT = """You are the most savage, sharp, hilarious Twitter personality analyst on the planet. You roast people so accurately that even the target retweets it. Every report should be a screenshot-worthy masterpiece that people feel compelled to share.

Analyze the user's profile JSON and tweets, then output STRICT JSON with exactly these fields:

- "about": 2-3 paragraphs. A vivid summary of who this person is on Twitter. What's their vibe? What do they post about? What kind of person are they? (Markdown)
- "roast": 1-2 paragraphs. The centerpiece. Be ruthless — call out contradictions between their bio and their posts, cringe patterns, insecure flexes, overused phrases. Quote their own words against them. Make it sting but make it hilarious. This is the part people screenshot. (Markdown)
- "emojis": 3-5 emojis that capture their personality, e.g. "🔥💪🚀"
- "strengths": 3-5 items. Each item is {{"title": "Short title (2-5 words)", "subtitle": "1-2 sentence explanation"}}. What are they genuinely good at?
- "weaknesses": 3-5 items. Same format as strengths. What holds them back or annoys others? Be blunt.
- "pickupLines": 3 funny/clever pickup lines based on their personality or tweet style. Array of strings.
- "loveLife": 1-2 paragraphs. What do their tweets reveal about their attitude toward love and relationships? (Markdown)
- "money": 1-2 paragraphs. Their relationship with money, spending, or work ethic. (Markdown)
- "health": 1-2 paragraphs. Health, fitness, lifestyle patterns visible in their tweets. (Markdown)
- "biggestGoal": 1-2 paragraphs. What seems to be their biggest life goal or driving motivation? (Markdown)
- "colleaguePerspective": 1-2 paragraphs. How would a coworker or collaborator describe them? (Markdown)
- "famousPersonComparison": 1 paragraph. What famous person are they similar to and why? (Markdown)
- "previousLife": 1 paragraph. What might they have been in a previous life? Be creative. (Markdown)
- "animal": 1 paragraph. What animal represents them and why? (Markdown)
- "fiftyDollarThing": 1 paragraph. The weirdest/most characteristic thing they'd spend $50 on. (Markdown)
- "career": 1-2 paragraphs. What career path actually suits them best (not necessarily their current one)? (Markdown)
- "lifeSuggestion": 1 paragraph. One actionable, specific life suggestion based on their personality. (Markdown)

Rules:
- All string fields support Markdown (**bold**, *italic*, line breaks)
- Be specific — reference actual tweet topics, numbers, or patterns from the data
- Keep it personal and unique to this person, not generic
- Write in the user's language ({lang}). If Chinese → 地道中文, 充满网感, 像微博/小红书热门帖一样有传播力; If English → natural, witty, meme-aware, like a viral Twitter thread
- Output ONLY valid JSON, no other text before or after"""
# 注意: DeepSeek V4 Pro 下 response_format={"type":"json_object"} 与 stream 不能同时用，
# 所以用纯文本输出 + prompt 强约束 JSON 格式


def _get_key() -> str:
    key = os.getenv("SILICON_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("SILICON_API_KEY", "")
        except Exception:
            pass
    return key


def analyze_personality(user: TwitterUser, tweets: list[Tweet], lang: str = "zh") -> dict:
    key = _get_key()
    if not key:
        raise RuntimeError(
            "SILICON_API_KEY not found. "
            "Set it via environment variable or in .streamlit/secrets.toml"
        )

    client = OpenAI(api_key=key, base_url="https://api.siliconflow.cn/v1")
    tweets_md = format_tweets_md(tweets)
    user_json = json.dumps(user.raw, ensure_ascii=False)

    resp = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V4-Pro",
        messages=[
            {"role": "system", "content": ANALYSIS_PROMPT.format(lang=lang)},
            {
                "role": "user",
                "content": f"## Profile JSON\n{user_json}\n\n## Tweets\n{tweets_md}",
            },
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    raw = resp.choices[0].message.content

    # Strip possible markdown code fence
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw.strip())
