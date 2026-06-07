import streamlit as st
from pathlib import Path
from i18n import _


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<style>"
            "section[data-testid='stSidebar'] > div:first-child { display: flex; flex-direction: column; min-height: calc(100vh - 4rem); }"
            "section[data-testid='stSidebar'] > div:first-child > div:nth-child(2) { flex: 1; }"
            "</style>",
            unsafe_allow_html=True,
        )

        st.page_link("streamlit_app.py", label=_("nav_home"))
        st.page_link("pages/1_Analysis.py", label=_("nav_analysis"))

        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

        gzh = Path(__file__).resolve().parent.parent / "gzh.jpg"
        if gzh.exists():
            st.image(str(gzh), width=150)
            st.markdown(
                "<p style='text-align:left;color:#9ca3af;font-size:0.85rem;margin-top:0.3rem;'>公众号-反馈/建议/防失联</p>",
                unsafe_allow_html=True,
            )
