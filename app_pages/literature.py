"""Page 6 — Literature Archive (delegates to the existing module)."""

import streamlit as st


def render() -> None:
    try:
        from literature_archive import render_literature_archive
        render_literature_archive()
    except ImportError as e:
        st.error(
            f"Literature Archive module not available.\n\n"
            f"Please install required dependencies: `pip install pyyaml`\n\n"
            f"```\n{e}\n```"
        )
