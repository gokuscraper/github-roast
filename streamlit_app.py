import base64
import threading
from pathlib import Path

import streamlit as st

_logo_path = Path(__file__).parent / "xpose-logo.jpg"
if _logo_path.exists():
    _jpg_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    _icon = f"data:image/jpeg;base64,{_jpg_b64}"
else:
    _icon = "🛠️"

st.set_page_config(
    page_title="X-POSE | 悟空X照妖镜",
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


@st.cache_resource
def get_global_limiter():
    return threading.BoundedSemaphore(value=1)


def _init():
    defaults = {
        "lang": "zh",
        "scraped_user": None,
        "scraped_tweets": None,
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
    logo_path = Path(__file__).parent / "xpose-logo.jpg"
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
    username = st.text_input(
        _("input_username_label"),
        placeholder="@username 或 https://x.com/username",
        key="home_username",
        label_visibility="collapsed",
    ).strip().removeprefix("https://x.com/").removeprefix("https://twitter.com/").lstrip("@")

col_btn, _btn_spacer = st.columns([1, 1])
with col_btn:
    if st.button(_("btn_analyze"), type="primary", use_container_width=True):
        if not username:
            st.warning(_("warn_empty_username"))
        else:
            sem = get_global_limiter()
            can_run = sem.acquire(blocking=False)
            if not can_run:
                st.warning(_("warn_concurrency"))
            else:
                try:
                    from scraper import fetch_all

                    with st.spinner(_("spinner_scraping")):
                        st.info(_("scrape_user") + f" @{username}...")
                        user, tweets = fetch_all(username)

                    st.session_state.scraped_user = user
                    st.session_state.scraped_tweets = tweets
                    st.session_state.analysis_result = None
                    st.session_state.scrape_username = username

                except Exception as e:
                    st.error(f"❌ {e}")
                finally:
                    sem.release()

# 爬取成功后在顶层显示跳转按钮（避免嵌套 button 导致无法点击）
if st.session_state.get("scraped_user") is not None:
    uname = st.session_state.scrape_username
    st.success(
        f"✅ @{uname} — {len(st.session_state.scraped_tweets)} tweets scraped"
    )
    if st.button(_("goto_analysis"), type="primary", use_container_width=True):
        st.switch_page("pages/1_Analysis.py")

st.divider()
st.caption(_("footer"))
