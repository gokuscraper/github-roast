import streamlit as st
import json
from urllib.parse import quote

from i18n import _
from lib.tweet_utils import summarize_tweets
from lib.sidebar import render_sidebar

render_sidebar()

raw = st.session_state.get("scraped_user")
if raw is None or isinstance(raw, tuple):
    st.warning(_("warn_no_session"))
    st.page_link("streamlit_app.py", label=_("goto_home"), use_container_width=True)
    st.stop()

user = st.session_state.scraped_user
tweets = st.session_state.scraped_tweets
result = st.session_state.analysis_result

CARD_CONFIG = [
    ("roast",         "🔥", "#e53e3e",  True,  "str"),
    ("strengths",     "💪", "#dd6b20",  False, "list"),
    ("weaknesses",    "😴", "#3182ce",  False, "list"),
    ("loveLife",      "❤️", "#e53e3e",  False, "str"),
    ("money",         "💰", "#38a169",  False, "str"),
    ("health",        "🏥", "#5a67d8",  False, "str"),
    ("colleaguePerspective", "👥", "#d69e2e", False, "str"),
    ("biggestGoal",   "🚀", "#805ad5",  False, "str"),
    ("famousPersonComparison", "⭐", "#38a169", False, "str"),
    ("pickupLines",   "💬", "#d53f8c",  False, "arr"),
    ("previousLife",  "🙏", "#718096",  False, "str"),
    ("animal",        "🐾", "#00a3c4",  False, "str"),
    ("fiftyDollarThing", "👛", "#d53f8c", False, "str"),
    ("career",        "💡", "#d69e2e",  False, "str"),
    ("lifeSuggestion","🌱", "#319795",  False, "str"),
]


def _md(t):
    import re
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    t = re.sub(r"\n", "<br>", t)
    return t


def _fmt_content(fmt, val):
    if fmt == "str":
        return _md(str(val))
    if fmt == "arr":
        items = val if isinstance(val, list) else []
        return "<ul style='list-style:none;padding:0;margin:0;'>" + \
               "".join(f"<li style='margin-bottom:0.4rem;'>{_md(str(i))}</li>" for i in items) + "</ul>"
    if fmt == "list":
        items = val if isinstance(val, list) else []
        return "<ul style='list-style:none;padding:0;margin:0;'>" + \
               "".join(
                   f"<li style='margin-bottom:0.6rem;'><strong>{_md(str(i.get('title','')))}:</strong> {_md(str(i.get('subtitle','')))}</li>"
                   for i in items
               ) + "</ul>"
    return str(val)


def _render_card(key_label, emoji, color, wide, fmt, data):
    html = _card_html(key_label, emoji, color, wide, fmt, data)
    if html:
        st.markdown(html, unsafe_allow_html=True)


def _card_html(key_label, emoji, color, wide, fmt, data):
    val = data.get(key_label) if isinstance(data, dict) else None
    # key_label is already translated; data keys are in English
    eng_key = [k for k, *_rest in CARD_CONFIG if _("card_" + k) == key_label]
    eng_key = eng_key[0] if eng_key else key_label
    val = data.get(eng_key) if isinstance(data, dict) else data
    if not val:
        return ""
    border_c = color + "44"
    col_span = "grid-column: 1 / -1;" if wide else ""
    return f"""
    <div style="border:1px solid {border_c};border-radius:16px;padding:1.2rem 1.5rem;
                background:{color}06;height:100%;{col_span}">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
            <span style="font-size:1.3rem;">{emoji}</span>
            <span style="font-weight:600;font-size:1rem;color:{color};">{key_label}</span>
        </div>
        <div style="border-bottom:1px solid #e5e7eb;margin-bottom:0.8rem;"></div>
        <div style="color:#374151;font-size:0.95rem;line-height:1.7;">{_fmt_content(fmt, val)}</div>
    </div>"""


def _build_report_html(result: dict, username: str, display_name: str = "", avatar_url: str = "") -> str:
    # Build each card HTML
    cards = ""
    for key, emoji, color, wide, fmt in CARD_CONFIG:
        val = result.get(key)
        if not val:
            continue
        border_c = color + "44"
        col_span = "grid-column: 1 / -1;" if wide else ""
        content = _fmt_content(fmt, val)
        # Escape {} to avoid breaking the outer f-string
        content = content.replace("{", "{{").replace("}", "}}")
        card_fmt = _("card_" + key)
        cards += (
            '<div class="card" style="border:1px solid ' + border_c
            + ';border-radius:16px;padding:1.2rem 1.5rem;background:' + color
            + '08;' + col_span + '">'
            '<div class="card-header">'
            '<span class="card-emoji">' + emoji + '</span>'
            '<span class="card-label" style="color:' + color + ';">' + card_fmt + '</span>'
            '</div>'
            '<div class="card-divider"></div>'
            '<div class="card-body">' + content + '</div>'
            '</div>'
        )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        background:#fafafa; padding:20px; }}
.banner {{ text-align:center; font-size:1.4rem; font-weight:700; margin-bottom:1.5rem;
           color:#1f2937; display:flex; align-items:center; justify-content:center; gap:0.5rem; }}
.banner-avatar {{ width:40px; height:40px; border-radius:50%; }}
.banner-name {{ }}
.banner-username {{ color:#9ca3af; font-weight:400; font-size:1rem; }}
.card-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(380px,1fr));
             gap:1.5rem; max-width:900px; margin:0 auto; }}
.card {{ }}
.card-header {{ display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; }}
.card-emoji {{ font-size:1.3rem; }}
.card-label {{ font-weight:600; font-size:1rem; }}
.card-divider {{ border-bottom:1px solid #e5e7eb; margin-bottom:0.8rem; }}
.card-body {{ color:#374151; font-size:0.95rem; line-height:1.7; }}
.card-body ul {{ list-style:none; padding:0; margin:0; }}
.card-body li {{ margin-bottom:0.4rem; }}
.card-body strong {{ font-weight:600; }}
.report-footer {{ text-align:center; margin-top:2rem; padding-top:1rem; border-top:1px solid #e5e7eb; color:#9ca3af; font-size:0.85rem; }}
.toolbar {{ text-align:center; margin-top:2rem; }}
.btn-download {{ background:#dc2626; color:#fff; border:none; border-radius:8px;
                 padding:0.75rem 2rem; font-size:1rem; font-weight:600; cursor:pointer;
                 box-shadow:0 2px 8px rgba(220,38,38,0.4); }}
.btn-download:hover {{ background:#ef4444; }}
</style>
</head>
<body>
<div id="report">
    <div class="banner">
        <img src="{avatar_url}" class="banner-avatar" onerror="this.style.display='none'">
        <span class="banner-name">{display_name}</span>
        <span class="banner-username">@{username}</span>
        &mdash; {_("report_title")}
    </div>
    <div class="card-grid">{cards}</div>
    <div class="report-footer">Powered by X-POSE (X照妖镜) | xpose7.streamlit.app</div>
</div>
<div class="toolbar">
    <button class="btn-download" onclick="capture()">{_("btn_download")}</button>
</div>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script>
function capture() {{
    html2canvas(document.getElementById('report'), {{ scale:2, useCORS:true }})
        .then(function(canvas) {{
            var link = document.createElement('a');
            link.download = '{username}_report.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }})
        .catch(function(err) {{
            document.getElementById('err').textContent = '截图失败: ' + err.message;
        }});
}}
</script>
<p id="err" style="color:red;text-align:center;margin-top:0.5rem;"></p>
</body>
</html>"""


def _on_analyze():
    from lib.ai import analyze_personality
    from scraper import shutdown

    with st.spinner(_("spinner_ai")):
        shutdown()
        try:
            r = analyze_personality(user, tweets, lang=st.session_state.get("lang", "zh"))
            st.session_state.analysis_result = r
            st.rerun()
        except Exception as e:
            st.error(f"AI analysis failed: {e}")


# ====== PAGE LAYOUT ======

st.markdown(
    f"<h1 style='margin-bottom:0;'>{_('analysis_title')}</h1>",
    unsafe_allow_html=True,
)
st.caption(f"@{user.username}")


# Profile card
with st.container():
    cols = st.columns([1, 4])
    with cols[0]:
        if user.avatar:
            st.image(user.avatar, width=96)
    with cols[1]:
        name = user.name or user.username
        bio = (user.bio[:150] + "...") if len(user.bio) > 150 else user.bio
        st.markdown(f"**<span style='font-size:1.3rem'>{name}</span>**", unsafe_allow_html=True)
        st.caption(f"@{user.username}")
        if user.location:
            st.caption(f"📍 {user.location}")
        st.markdown(bio)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric(_("label_followers"), f"{user.followers:,}")
    s2.metric(_("label_following"), f"{user.following:,}")
    s3.metric(_("label_tweets"), f"{user.tweets_count:,}")
    s4.metric(_("label_verified"), "✅" if user.verified else "—")

st.divider()

# Tweet stats
summary = summarize_tweets(tweets)
if summary["count"]:
    st.markdown(f"### 📊 {_('tweet_stats')}")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric(_("stat_count"), summary["count"])
    r2.metric(_("stat_avg_likes"), f"{summary['avg_likes']:,}")
    r3.metric(_("stat_max_likes"), f"{summary['max_likes']:,}")
    r4.metric(_("stat_avg_views"), f"{summary['avg_views']:,}")
    r5.metric(_("stat_total_rts"), f"{summary['total_retweets']:,}")
    st.divider()

# AI Analysis
st.markdown(f"### ✨ {_('ai_section_title')}")

if result:
    emojis = result.get("emojis", "")
    if emojis:
        st.markdown(
            f"<p style='text-align:center;font-size:2.5rem;letter-spacing:0.3rem;'>{emojis}</p>",
            unsafe_allow_html=True,
        )

    about = result.get("about", "")
    if about:
        st.markdown(
            f"<div style='max-width:700px;margin:0 auto 2rem auto;text-align:center;color:#4b5563;font-size:1rem;'>{_md(about)}</div>",
            unsafe_allow_html=True,
        )

    # Share to X
    share_txt = _("share_text").format(user=user.username)
    share_url = f"https://twitter.com/intent/tweet?text={quote(share_txt)}"
    c1, c2 = st.columns([1, 8])
    with c1:
        st.link_button(_("share_x"), share_url)

    # Build report HTML with cards + screenshot button
    report_html = _build_report_html(result, user.username, user.name, user.avatar)
    st.components.v1.html(report_html, height=1800, scrolling=True)

    st.divider()
    if st.button(_("btn_rerun_ai"), use_container_width=True):
        st.session_state.analysis_result = None
        st.rerun()
else:
    st.info(_("ai_hint"))
    if st.button(_("btn_run_ai"), type="primary", use_container_width=True):
        _on_analyze()

# Footer nav
st.divider()
st.page_link("streamlit_app.py", label=_("goto_home"), use_container_width=True)
