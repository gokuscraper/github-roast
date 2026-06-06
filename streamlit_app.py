import base64
from pathlib import Path

import streamlit as st

_logo_path = Path(__file__).parent / "groast-logo.jpg"
if _logo_path.exists():
    _jpg_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    _icon = f"data:image/jpeg;base64,{_jpg_b64}"
else:
    _icon = "🛠️"

st.set_page_config(
    page_title="Github-Roast | 悟空Github照妖镜",
    page_icon=_icon,
    layout="wide",
)

st.markdown(
    """
    <style>
    #MainMenu, .stDeployButton, [data-testid="stStatusWidget"], [data-testid="stSidebarNav"] { visibility: hidden; display: none; }
    div[data-testid="stTextInput"] { min-width: 380px; }
    </style>
    """,
    unsafe_allow_html=True,
)

from i18n import _


def _init():
    defaults = {
        "lang": "zh",
        "scraped_user": None,
        "scraped_repos": None,
        "scraped_events": None,
        "analysis_result": None,
        "scrape_username": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()

from lib.sidebar import render_sidebar
render_sidebar()

title_col, title_col3 = st.columns([10, 5])
with title_col:
    logo_html = ""
    logo_path = Path(__file__).parent / "groast-logo.jpg"
    if logo_path.exists():
        b64 = base64.b64encode(logo_path.read_bytes()).decode()
        logo_html = f'<img src="data:image/jpeg;base64,{b64}" style="width:42px;height:42px;vertical-align:middle;margin-right:10px;">'
    st.markdown(
        f"<h1 style='margin:0;display:flex;align-items:center;'>{logo_html}{_('title')}</h1>",
        unsafe_allow_html=True,
    )

with title_col3:
    lang_opts = {"简体中文": "zh", "English": "en"}
    idx = list(lang_opts.values()).index(st.session_state.lang)
    sel = st.radio(
        "Lang",
        options=list(lang_opts.keys()),
        index=idx,
        horizontal=True,
        label_visibility="collapsed",
    )
    if lang_opts[sel] != st.session_state.lang:
        st.session_state.lang = lang_opts[sel]
        st.rerun()

st.divider()

st.markdown(f"### {_('home_heading')}")
st.caption(_("home_desc"))

col_in, _col_spacer = st.columns([3, 1])
with col_in:
    raw_input = st.text_input(
        _("input_username_label"),
        placeholder=_("input_username_placeholder"),
        key="home_username",
        label_visibility="collapsed",
    ).strip().lstrip("@").rstrip("/")
    username = raw_input.removeprefix("https://github.com/").removeprefix("http://github.com/").removeprefix("github.com/")
    # 如果是仓库链接 (user/repo)，只取前面的用户名
    username = username.split("/")[0]

col_btn, _btn_spacer = st.columns([1, 1])
with col_btn:
    if st.button(_("btn_analyze"), type="primary", use_container_width=True):
        if not username:
            st.warning(_("warn_empty_username"))
        else:
            try:
                from github_scraper import fetch_all

                with st.spinner(_("spinner_scraping")):
                    st.info(_("scrape_user") + f" @{username}...")
                    user, repos, events = fetch_all(username)

                st.session_state.scraped_user = user
                st.session_state.scraped_repos = repos
                st.session_state.scraped_events = events
                st.session_state.analysis_result = None
                st.session_state.scrape_username = username

            except Exception as e:
                st.error(f"❌ {e}")

if st.session_state.get("scraped_user") is not None:
    uname = st.session_state.scrape_username
    repos = st.session_state.scraped_repos or []
    events = st.session_state.scraped_events or []
    st.success(
        f"✅ {uname} — {len(repos)} repos, {len(events)} events"
    )
    if st.button(_("goto_analysis"), type="primary", use_container_width=True):
        st.switch_page("pages/1_Analysis.py")

st.divider()
st.caption(_("footer"))
