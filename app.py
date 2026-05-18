"""QHED-BR Streamlit entry point.

Each page lives in ``app_pages/``; this script wires them together via
``st.navigation`` so that nav labels can be translated at runtime.
"""

from __future__ import annotations

import sys
import traceback

import matplotlib
matplotlib.use("Agg")
import streamlit as st

st.set_page_config(
    page_title="QHED-BR: Quantum Edge Detection",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from app_pages import circuit, complexity, edge_detection, home, ibm_hardware, literature, overview
    from ui.i18n import render_lang_switcher, t
except Exception:
    st.error(
        f"Failed to import application modules.\n\n"
        f"**Python {sys.version}**\n\n"
        f"```\n{traceback.format_exc()}\n```"
    )
    st.stop()


render_lang_switcher(location=st.sidebar)
st.sidebar.title(t("nav.title"))

pages = [
    st.Page(home.render,            title=t("nav.home"),           url_path="home",          default=True),
    st.Page(overview.render,        title=t("nav.overview"),       url_path="overview"),
    st.Page(circuit.render,         title=t("nav.circuit"),        url_path="circuit"),
    st.Page(edge_detection.render,  title=t("nav.edge_detection"), url_path="edge-detection"),
    st.Page(complexity.render,      title=t("nav.complexity"),     url_path="complexity"),
    st.Page(ibm_hardware.render,    title=t("nav.ibm"),            url_path="ibm-hardware"),
    st.Page(literature.render,      title=t("nav.literature"),     url_path="literature"),
]

nav = st.navigation(pages, position="sidebar")
nav.run()
