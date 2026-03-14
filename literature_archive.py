"""
Literature Archive Page for QHED-BR Streamlit App
===================================================
QED prior research archive viewer.
Provides search, filter, detail view, and figure gallery.
"""

import os
import yaml
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), "research_archive", "qed")
INDEX_PATH = os.path.join(ARCHIVE_DIR, "index.yaml")


# ---------------------------------------------------------------------------
# Data Loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_index():
    """Load and parse the archive index.yaml."""
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@st.cache_data
def load_entry_markdown(entry_path):
    """Load a single entry's markdown file."""
    full_path = os.path.join(ARCHIVE_DIR, entry_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def load_svg(svg_path):
    """Load SVG file content for inline display."""
    full_path = os.path.join(ARCHIVE_DIR, svg_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


# ---------------------------------------------------------------------------
# Helper: tag display
# ---------------------------------------------------------------------------
def render_tag(label, value, color="#4A90D9"):
    """Render a colored tag badge."""
    if isinstance(value, list):
        value = ", ".join(value)
    return (
        f'<span style="background-color:{color};color:white;'
        f'padding:2px 8px;border-radius:10px;font-size:0.78em;'
        f'margin-right:4px;font-weight:500;">{label}: {value}</span>'
    )


TAG_COLORS = {
    "encoding": "#7B68EE",
    "edge_definition": "#E74C3C",
    "circuit_type": "#E67E22",
    "noise_awareness": "#27AE60",
    "evaluation": "#4A90D9",
}


# ---------------------------------------------------------------------------
# Main page renderer
# ---------------------------------------------------------------------------
def render_literature_archive():
    """Render the full Literature Archive page."""
    st.title("Quantum Edge Detection — Literature Archive")
    st.markdown(
        "A curated archive of QED prior research organized with a unified analysis template. "
        "Use the sidebar to filter by tags, year, or keywords, and expand entries for detailed analysis."
    )
    st.markdown("---")

    # Load index
    try:
        index_data = load_index()
    except FileNotFoundError:
        st.error(f"Index file not found: {INDEX_PATH}")
        return
    except Exception as e:
        st.error(f"Error loading index: {e}")
        return

    entries = index_data.get("entries", [])
    tag_schema = index_data.get("tag_schema", {})

    if not entries:
        st.warning("No entries found in the archive.")
        return

    # -----------------------------------------------------------------
    # Sidebar filters
    # -----------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Archive Filters")

    # Keyword search
    search_query = st.sidebar.text_input(
        "Keyword Search",
        placeholder="Title, summary, tags...",
        key="archive_search",
    )

    # Year filter
    all_years = sorted(set(e.get("year", 0) for e in entries), reverse=True)
    selected_years = st.sidebar.multiselect(
        "Year", options=all_years, default=[], key="archive_year"
    )

    # Tag filters
    filter_encoding = st.sidebar.multiselect(
        "Encoding",
        options=tag_schema.get("encoding", []),
        default=[],
        key="archive_enc",
    )
    filter_edge = st.sidebar.multiselect(
        "Edge Definition",
        options=tag_schema.get("edge_definition", []),
        default=[],
        key="archive_edge",
    )
    filter_circuit = st.sidebar.multiselect(
        "Circuit Type",
        options=tag_schema.get("circuit_type", []),
        default=[],
        key="archive_circuit",
    )
    filter_noise = st.sidebar.multiselect(
        "Noise Awareness",
        options=tag_schema.get("noise_awareness", []),
        default=[],
        key="archive_noise",
    )

    # -----------------------------------------------------------------
    # Filter entries
    # -----------------------------------------------------------------
    filtered = []
    for entry in entries:
        tags = entry.get("tags", {})

        # Year filter
        if selected_years and entry.get("year") not in selected_years:
            continue

        # Tag filters
        if filter_encoding and tags.get("encoding") not in filter_encoding:
            continue
        if filter_edge and tags.get("edge_definition") not in filter_edge:
            continue
        if filter_circuit and tags.get("circuit_type") not in filter_circuit:
            continue
        if filter_noise and str(tags.get("noise_awareness")) not in filter_noise:
            continue

        # Keyword search (title + summary + tags)
        if search_query:
            query_lower = search_query.lower()
            searchable = " ".join([
                entry.get("title", ""),
                entry.get("summary", ""),
                str(tags),
                " ".join(entry.get("authors", [])),
            ]).lower()
            if query_lower not in searchable:
                continue

        filtered.append(entry)

    # -----------------------------------------------------------------
    # Summary metrics
    # -----------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Papers", len(entries))
    col2.metric("Filtered", len(filtered))
    col3.metric("Year Range",
                f"{min(e['year'] for e in entries)}–{max(e['year'] for e in entries)}"
                if entries else "N/A")

    st.markdown("---")

    # -----------------------------------------------------------------
    # Overview diagrams (collapsible)
    # -----------------------------------------------------------------
    with st.expander("Overview Diagrams (QED Pipeline & Comparison)", expanded=False):
        diagram_files = [
            ("QED Pipeline Overview", "figures/qed_pipeline_overview.svg"),
            ("QHED Circuit Architecture", "figures/qhed_circuit_blocks.svg"),
            ("Approaches Comparison", "figures/qed_comparison_table.svg"),
        ]
        for title, svg_path in diagram_files:
            full_path = os.path.join(ARCHIVE_DIR, svg_path)
            if os.path.exists(full_path):
                st.markdown(f"**{title}**")
                st.image(full_path, use_container_width=True)
                st.markdown("")

    st.markdown("---")

    # -----------------------------------------------------------------
    # Paper list
    # -----------------------------------------------------------------
    if not filtered:
        st.info("No papers match the current filters. Adjust the sidebar filters to see results.")
        return

    st.subheader(f"Papers ({len(filtered)})")

    for entry in filtered:
        tags = entry.get("tags", {})

        # Card-style display
        with st.container():
            st.markdown(
                f"### {entry.get('title', 'Untitled')}\n"
                f"**{', '.join(entry.get('authors', [])[:3])}"
                f"{'  et al.' if len(entry.get('authors', [])) > 3 else ''}** "
                f"| {entry.get('venue', '')} ({entry.get('year', '')})"
            )

            # Tags row
            tag_html = ""
            for key, color in TAG_COLORS.items():
                val = tags.get(key)
                if val:
                    tag_html += render_tag(key.replace("_", " "), val, color)
            if tag_html:
                st.markdown(tag_html, unsafe_allow_html=True)

            # Summary
            summary = entry.get("summary", "").strip()
            if summary:
                st.markdown(f"> {summary}")

            # DOI link
            doi = entry.get("doi", "")
            if doi:
                st.markdown(f"DOI: [{doi}](https://doi.org/{doi})")

            # Detail expander
            with st.expander("Detail View", expanded=False):
                entry_path = entry.get("entry_path", "")
                md_content = load_entry_markdown(entry_path)
                if md_content:
                    st.markdown(md_content, unsafe_allow_html=True)
                else:
                    st.warning(f"Entry file not found: {entry_path}")

                # Figure gallery
                figures = entry.get("figures", [])
                if figures:
                    st.markdown("#### Figures")
                    for fig_path in figures:
                        full_fig = os.path.join(ARCHIVE_DIR, fig_path)
                        if os.path.exists(full_fig):
                            st.image(full_fig, use_container_width=True)
                        else:
                            st.caption(f"(Figure not found: {fig_path})")

            st.markdown("---")

    # -----------------------------------------------------------------
    # Footer / usage guide
    # -----------------------------------------------------------------
    with st.expander("Usage & Development Guide"):
        st.markdown("""
### Running Locally

```bash
# Install dependencies
pip install streamlit pyyaml matplotlib numpy

# Generate diagrams (first time only)
python research_archive/qed/generate_figures.py

# Run the Streamlit app
streamlit run app.py
```

### Adding a New Paper

1. Create a new folder under `research_archive/qed/entries/` (e.g., `author2024_topic/`)
2. Copy `TEMPLATE.md` as `entry.md` and fill in all sections (A through K)
3. Add the entry metadata to `research_archive/qed/index.yaml`
4. (Optional) Add related figures to `figures/`

### Directory Structure

```
research_archive/qed/
├── TEMPLATE.md              # Unified analysis template
├── index.yaml               # Metadata index
├── generate_figures.py      # SVG diagram generation script
├── entries/
│   ├── yao2017_qhed/
│   │   └── entry.md
│   ├── zhang2015_neqr_edge/
│   │   └── entry.md
│   └── ...                  # More entries
└── figures/
    ├── qed_pipeline_overview.svg
    ├── qhed_circuit_blocks.svg
    └── qed_comparison_table.svg
```
        """)
