import streamlit as st
from urllib.parse import quote

from i18n import _
from lib.repo_utils import summarize_repos
from lib.sidebar import render_sidebar

render_sidebar()

raw = st.session_state.get("scraped_user")
if raw is None or isinstance(raw, tuple):
    st.warning(_("warn_no_session"))
    st.page_link("streamlit_app.py", label=_("goto_home"), use_container_width=True)
    st.stop()

user = st.session_state.scraped_user
repos = st.session_state.scraped_repos or []
events = st.session_state.scraped_events or []
result = st.session_state.analysis_result

CARD_CONFIG = [
    ("roast",              "🔥", "#e53e3e",  True,  "str"),
    ("techStack",          "💻", "#dd6b20",  False, "list"),
    ("weaknesses",         "😴", "#3182ce",  False, "list"),
    ("openSourceInfluence","⭐", "#38a169",  False, "str"),
    ("projectHighlights",  "🚀", "#805ad5",  False, "str"),
    ("collaborationStyle", "👥", "#d69e2e",  False, "str"),
    ("activityPulse",      "📊", "#0ea5e9",  False, "str"),
    ("careerAdvice",       "💡", "#d53f8c",  False, "str"),
    ("achievements",       "🏅", "#5a67d8",  False, "arr"),
    ("lifeSuggestion",     "🌱", "#319795",  True,  "str"),
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


def _build_report_html(result: dict, user, summary: dict) -> str:
    login = user.login
    display_name = user.name or user.login
    avatar_url = user.avatar_url

    bio = (user.bio[:200] + "...") if len(user.bio) > 200 else user.bio
    meta_parts = []
    if user.company:
        meta_parts.append(f"🏢 {user.company}")
    if user.location:
        meta_parts.append(f"📍 {user.location}")
    if user.created_at:
        meta_parts.append(f"📅 {user.created_at[:10]}")
    if user.blog:
        meta_parts.append(f"🔗 {user.blog[:40]}")
    meta_html = f'<div style="color:#6b7280;font-size:0.9rem;margin:0.3rem 0;">{" | ".join(meta_parts)}</div>' if meta_parts else ""

    stats_row = f"""<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:1rem;
        padding:1rem;background:#f9fafb;border-radius:12px;text-align:center;">
        <div><div style="font-size:1.3rem;font-weight:700;">{user.followers:,}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("label_followers")}</div></div>
        <div><div style="font-size:1.3rem;font-weight:700;">{user.following:,}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("label_following")}</div></div>
        <div><div style="font-size:1.3rem;font-weight:700;">{user.public_repos:,}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("label_repos")}</div></div>
        <div><div style="font-size:1.3rem;font-weight:700;">{user.public_gists:,}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("label_gists")}</div></div>
    </div>"""

    repo_stats_html = ""
    if summary["repos_count"]:
        repo_stats_html = f"""<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.8rem;margin-top:0.8rem;
            padding:1rem;background:#f9fafb;border-radius:12px;text-align:center;">
            <div><div style="font-size:1.1rem;font-weight:600;">{summary["repos_count"]}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("stat_repos")}</div></div>
            <div><div style="font-size:1.1rem;font-weight:600;">{summary["total_stars"]:,}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("stat_total_stars")}</div></div>
            <div><div style="font-size:1.1rem;font-weight:600;">{summary["languages_count"]}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("stat_languages")}</div></div>
            <div><div style="font-size:1.1rem;font-weight:600;">{summary["events_count"]}</div><div style="font-size:0.8rem;color:#9ca3af;">{_("stat_events")}</div></div>
        </div>"""

    raw_value = summary.get("account_value", 0)
    is_zh = st.session_state.get("lang", "zh") == "zh"
    currency = "¥" if is_zh else "$"
    value = raw_value if is_zh else round(raw_value / 7)
    value_label = _("label_account_value")
    value_html = f"""<div style="text-align:center;margin-top:1rem;padding:0.8rem;background:linear-gradient(135deg,#fef3c7,#fde68a);border-radius:12px;font-size:1.1rem;font-weight:700;">
  {value_label} <span style="font-size:1.4rem;">{currency}{value:,}</span>
</div>"""

    emojis = result.get("emojis", "")
    about = result.get("about", "")
    about_html = _md(about) if about else ""
    title_text = result.get("title", "")
    footer_text = "Powered by Github-Roast (Github照妖镜) | groast.streamlit.app"

    section1 = f"""
    <div id="report-1" style="padding:20px;">
        <div style="text-align:center;font-size:1.6rem;font-weight:800;margin-bottom:1rem;color:#1f2937;">{title_text}</div>
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.5rem;">
            <img src="{avatar_url}" style="width:56px;height:56px;border-radius:50%;" onerror="this.style.display='none'">
            <div>
                <div style="font-size:1.4rem;font-weight:700;">{display_name}</div>
                <div style="color:#9ca3af;">@{login}</div>
            </div>
        </div>
        <div style="margin:0.5rem 0;color:#4b5563;">{bio}</div>
        {meta_html}
        {stats_row}
        <div style="font-size:1.1rem;font-weight:600;margin-top:1.5rem;color:#1f2937;">📊 {_("repo_stats")}</div>
        {repo_stats_html}
        {value_html}
        <div style="text-align:center;margin-top:1.5rem;">
            <div style="font-size:2.5rem;letter-spacing:0.3rem;">{emojis}</div>
            <div style="max-width:700px;margin:1rem auto;color:#4b5563;font-size:1rem;line-height:1.7;">{about_html}</div>
        </div>
        <div class="report-footer">{footer_text}</div>
    </div>"""

    card_groups = [CARD_CONFIG[:3], CARD_CONFIG[3:7], CARD_CONFIG[7:]]
    sections_html = []
    sec_ids = ["report-2", "report-3", "report-4"]
    for gi, group in enumerate(card_groups):
        cards_html = ""
        for ci, (key, emoji, color, wide, fmt) in enumerate(group):
            val = result.get(key)
            if not val:
                continue
            border_c = color + "44"
            col_span = "grid-column: 1 / -1;" if wide else ""
            content = _fmt_content(fmt, val)
            content = content.replace("{", "{{").replace("}", "}}")
            card_fmt = _("card_" + key)
            cards_html += (
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
        sec_id = sec_ids[gi]
        sections_html.append(f"""
    <div id="{sec_id}" style="padding:20px;">
        <div class="card-grid">{cards_html}</div>
        <div class="report-footer">{footer_text}</div>
    </div>""")

    buttons = f"""
    <div class="toolbar">
        <button class="btn-download" onclick="capture('report-1','{login}_1_profile')">{_("btn_section1")}</button>
        <button class="btn-download" onclick="capture('report-2','{login}_2_analysis_a')">{_("btn_section2")}</button>
        <button class="btn-download" onclick="capture('report-3','{login}_3_analysis_b')">{_("btn_section3")}</button>
        <button class="btn-download" onclick="capture('report-4','{login}_4_analysis_c')">{_("btn_section4")}</button>
        <button class="btn-download btn-all" onclick="downloadAll()">{_("btn_download_all")}</button>
    </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#fafafa; }}
.card-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(380px,1fr)); gap:1.5rem; max-width:900px; margin:0 auto; }}
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
.toolbar {{ text-align:center; padding:20px; display:flex; flex-wrap:wrap; justify-content:center; gap:0.5rem; }}
.btn-download {{ background:#dc2626; color:#fff; border:none; border-radius:8px; padding:0.6rem 1.2rem; font-size:0.9rem; font-weight:600; cursor:pointer; }}
.btn-download:hover {{ background:#ef4444; }}
.btn-all {{ background:#1f2937; }}
.btn-all:hover {{ background:#374151; }}
</style>
</head>
<body>
{section1}
{sections_html[0]}
{sections_html[1]}
{sections_html[2]}
{buttons}
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script>
var username = '{login}';
var avatarUrl = '{avatar_url}';
function capture(id, name) {{
    return html2canvas(document.getElementById(id), {{ scale:2, useCORS:true }})
        .then(function(canvas) {{
            var link = document.createElement('a');
            link.download = name + '.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }})
        .catch(function(err) {{ document.getElementById('err').textContent = '截图失败: ' + err.message; }});
}}
function downloadAvatar() {{
    return fetch(avatarUrl)
        .then(function(r) {{ return r.blob(); }})
        .then(function(blob) {{
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.download = username + '_1_avatar.png';
            a.href = url;
            a.click();
            URL.revokeObjectURL(url);
        }})
        .catch(function() {{}});
}}
function downloadAll() {{
    downloadAvatar()
        .then(function() {{ return capture('report-1', username + '_2_profile'); }})
        .then(function() {{ return capture('report-2', username + '_3_analysis_a'); }})
        .then(function() {{ return capture('report-3', username + '_4_analysis_b'); }})
        .then(function() {{ return capture('report-4', username + '_5_analysis_c'); }});
}}
</script>
<p id="err" style="color:red;text-align:center;padding:0 20px 20px;"></p>
</body>
</html>"""


def _on_analyze():
    from lib.ai import analyze_developer

    with st.spinner(_("spinner_ai")):
        try:
            r = analyze_developer(user, repos, events, lang=st.session_state.get("lang", "zh"))
            st.session_state.analysis_result = r
            st.rerun()
        except Exception as e:
            st.error(f"AI analysis failed: {e}")


# ====== PAGE LAYOUT ======

st.markdown(
    f"<h1 style='margin-bottom:0;'>{_('analysis_title')}</h1>",
    unsafe_allow_html=True,
)
st.caption(f"@{user.login}")

# Profile card
with st.container():
    cols = st.columns([1, 4])
    with cols[0]:
        if user.avatar_url:
            st.image(user.avatar_url, width=96)
    with cols[1]:
        name = user.name or user.login
        bio = (user.bio[:150] + "...") if len(user.bio) > 150 else user.bio
        st.markdown(f"**<span style='font-size:1.3rem'>{name}</span>**", unsafe_allow_html=True)
        st.caption(f"@{user.login}")
        meta_parts = []
        if user.company:
            meta_parts.append(f"🏢 {user.company}")
        if user.location:
            meta_parts.append(f"📍 {user.location}")
        if user.created_at:
            meta_parts.append(f"📅 {user.created_at[:10]}")
        if user.blog:
            meta_parts.append(f"🔗 {user.blog[:40]}")
        if meta_parts:
            st.caption(" | ".join(meta_parts))
        if bio:
            st.markdown(bio)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric(_("label_followers"), f"{user.followers:,}")
    s2.metric(_("label_following"), f"{user.following:,}")
    s3.metric(_("label_repos"), f"{user.public_repos:,}")
    s4.metric(_("label_gists"), f"{user.public_gists:,}")

st.divider()

# Repo stats
summary = summarize_repos(repos, events, followers=user.followers)
if summary["repos_count"]:
    st.markdown(f"### 📊 {_('repo_stats')}")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric(_("stat_repos"), summary["repos_count"])
    r2.metric(_("stat_total_stars"), f"{summary['total_stars']:,}")
    r3.metric(_("stat_languages"), summary["languages_count"])
    r4.metric(_("stat_events"), summary["events_count"])

    if summary["top_languages"]:
        st.caption(" | ".join(
            f"{l['name']} ({l['count']})" for l in summary["top_languages"][:6]
        ))
    st.divider()

# AI Analysis
st.markdown(f"### ✨ {_('ai_section_title')}")

if result:
    title = result.get("title", "")
    if title:
        st.markdown(
            f"<p style='text-align:center;font-size:2rem;font-weight:800;color:#1f2937;'>{title}</p>",
            unsafe_allow_html=True,
        )

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

    share_txt = _("share_text").format(user=user.login)
    share_url = f"https://twitter.com/intent/tweet?text={quote(share_txt)}"
    c1, c2 = st.columns([1, 8])
    with c1:
        st.link_button(_("share_x"), share_url)

    report_html = _build_report_html(result, user, summary)
    st.components.v1.html(report_html, height=1800, scrolling=True)

    st.divider()
    if st.button(_("btn_rerun_ai"), use_container_width=True):
        st.session_state.analysis_result = None
        st.rerun()
else:
    st.info(_("ai_hint"))
    if st.button(_("btn_run_ai"), type="primary", use_container_width=True):
        _on_analyze()

st.divider()
st.page_link("streamlit_app.py", label=_("goto_home"), use_container_width=True)
