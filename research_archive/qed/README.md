# QED Research Archive

A curated archive of prior research on Quantum Edge Detection (QED), organized with a unified analysis template.

## Directory Structure

```
research_archive/qed/
├── README.md                 # This file
├── TEMPLATE.md               # Unified analysis template (copy for new entries)
├── index.yaml                # Metadata index (used by Streamlit search/filter)
├── generate_figures.py       # SVG diagram generation script
├── entries/                  # Individual paper entries
│   ├── yao2017_qhed/
│   │   └── entry.md
│   ├── zhang2015_neqr_edge/
│   │   └── entry.md
│   ├── fan2019_quantum_laplacian/
│   │   └── entry.md
│   ├── yi2015_qsobel/
│   │   └── entry.md
│   ├── chetia2021_improved_sobel/
│   │   └── entry.md
│   ├── ma2022_eight_direction_sobel/
│   │   └── entry.md
│   ├── shubha2024_edge_quantumized/
│   │   └── entry.md
│   └── silver2022_hybrid_nisq/
│       └── entry.md
└── figures/                  # SVG diagrams
    ├── qed_pipeline_overview.svg
    ├── qhed_circuit_blocks.svg
    ├── qed_comparison_table.svg
    └── *.mmd                 # Mermaid source files
```

## Adding a New Paper

1. Create a new folder under `entries/` (e.g., `author2024_topic/`)
2. Copy `TEMPLATE.md` as `entry.md` and fill in all sections
3. Add the entry metadata to `index.yaml`
4. (Optional) Add related figures to `figures/`

## Regenerating Diagrams

```bash
python research_archive/qed/generate_figures.py
```

## Viewing in Streamlit

```bash
streamlit run app.py
# → Select "6. Literature Archive" in the sidebar
```
