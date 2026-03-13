"""
QED Research Archive - SVG Figure Generator
============================================
잘림/깨짐 방지 체크리스트 적용:
  - tight_layout() + bbox_inches="tight"
  - 충분한 figsize + padding
  - 축소해도 읽히는 폰트/선 두께
  - SVG 형식 우선
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Common style
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'DejaVu Sans',
    'axes.linewidth': 1.2,
    'lines.linewidth': 1.5,
})

COLORS = {
    'input':      '#4A90D9',
    'encoding':   '#7B68EE',
    'quantum':    '#E74C3C',
    'measure':    '#F39C12',
    'post':       '#27AE60',
    'output':     '#2C3E50',
    'bg':         '#FAFBFC',
    'arrow':      '#555555',
    'highlight':  '#FF6B6B',
}


def draw_rounded_box(ax, x, y, w, h, label, color, fontsize=10, text_color='white'):
    """Draw a rounded rectangle with centered text."""
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.12",
        facecolor=color, edgecolor='#333333', linewidth=1.5,
        alpha=0.92, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=text_color, zorder=3)


def draw_arrow(ax, x1, y1, x2, y2, color='#555555'):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8),
                zorder=1)


# ==========================================================================
# Figure 1: QED Full Pipeline Overview
# ==========================================================================
def generate_pipeline_overview():
    """QED 전체 파이프라인 다이어그램 (입력→인코딩→양자연산→측정→후처리→엣지맵)"""
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.set_xlim(-0.5, 15.5)
    ax.set_ylim(-2.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg'])

    # Title
    ax.text(7.5, 3.0, "Quantum Edge Detection (QED) Pipeline",
            ha='center', va='center', fontsize=16, fontweight='bold', color='#1a1a2e')

    # Pipeline stages
    stages = [
        (1.0,  0.5, 2.2, 1.4, "Classical\nImage\n(Input)", COLORS['input']),
        (4.0,  0.5, 2.2, 1.4, "Quantum State\nEncoding\n(Amplitude)", COLORS['encoding']),
        (7.5,  0.5, 2.8, 1.4, "Quantum Operation\n(H gate + D₂ₙ₋₁)", COLORS['quantum']),
        (11.0, 0.5, 2.2, 1.4, "Measurement\n& Post-\nselection", COLORS['measure']),
        (14.0, 0.5, 2.2, 1.4, "Edge Map\n(Output)", COLORS['post']),
    ]

    for (x, y, w, h, label, color) in stages:
        draw_rounded_box(ax, x, y, w, h, label, color, fontsize=9)

    # Arrows between stages
    arrow_pairs = [(2.1, 2.9), (5.1, 6.1), (8.9, 9.9), (12.1, 12.9)]
    for (x1, x2) in arrow_pairs:
        draw_arrow(ax, x1, 0.5, x2, 0.5)

    # Sub-details below
    details = [
        (1.0,  -1.5, "Grayscale\n2ᵏ × 2ᵏ pixels"),
        (4.0,  -1.5, "O(n²) gates\n2k+1 qubits"),
        (7.5,  -1.5, "O(k) gates\n(detection only)"),
        (11.0, -1.5, "Probability\n→ intensity"),
        (14.0, -1.5, "Threshold\n+ Boundary\nRestoration"),
    ]

    for (x, y, txt) in details:
        ax.text(x, y, txt, ha='center', va='center',
                fontsize=8, color='#555555', style='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0',
                          edgecolor='#cccccc', alpha=0.8))
        ax.annotate('', xy=(x, y + 0.45), xytext=(x, -0.2),
                    arrowprops=dict(arrowstyle='->', color='#aaaaaa',
                                   lw=1.0, linestyle='--'))

    plt.tight_layout(pad=1.0)
    path = os.path.join(FIGURES_DIR, "qed_pipeline_overview.svg")
    fig.savefig(path, format='svg', bbox_inches='tight', pad_inches=0.3)
    plt.close(fig)
    print(f"  [OK] {path}")
    return path


# ==========================================================================
# Figure 2: QHED Circuit Block Diagram
# ==========================================================================
def generate_circuit_block_diagram():
    """대표 알고리즘(QHED)의 회로 블록 다이어그램"""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(-0.5, 13.5)
    ax.set_ylim(-1.5, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg'])

    ax.text(6.5, 7.0, "QHED Circuit Architecture (Abstracted)",
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1a1a2e')

    # Qubit lines
    qubit_labels = [
        ("Ancilla  |0⟩", 5.5),
        ("Data q₁  |0⟩", 4.0),
        ("Data q₂  |0⟩", 2.5),
        ("  ...  ", 1.3),
        ("Data q₂ₖ |0⟩", 0.2),
    ]

    for (label, y) in qubit_labels:
        if "..." in label:
            ax.text(0.8, y, label, ha='center', va='center', fontsize=11, color='#888')
            continue
        ax.text(0.8, y, label, ha='right', va='center', fontsize=10,
                fontweight='bold', color='#333')
        ax.plot([1.0, 12.5], [y, y], color='#333', lw=1.0, zorder=0)

    # Block: Amplitude Encoding
    amp_box = FancyBboxPatch((1.8, -0.3), 2.4, 6.3,
                              boxstyle="round,pad=0.15",
                              facecolor=COLORS['encoding'], edgecolor='#333',
                              linewidth=1.5, alpha=0.25, zorder=1)
    ax.add_patch(amp_box)
    ax.text(3.0, 6.3, "Amplitude\nEncoding", ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['encoding'])
    ax.text(3.0, -0.7, "O(n²) gates", ha='center', va='center',
            fontsize=8, color='#666', style='italic')

    # Block: Hadamard on ancilla
    h_box = FancyBboxPatch((5.0, 5.0), 1.0, 1.0,
                            boxstyle="round,pad=0.08",
                            facecolor=COLORS['quantum'], edgecolor='#333',
                            linewidth=1.5, alpha=0.9, zorder=2)
    ax.add_patch(h_box)
    ax.text(5.5, 5.5, "H", ha='center', va='center',
            fontsize=14, fontweight='bold', color='white', zorder=3)

    # Block: D_{2n-1} on data qubits
    d_box = FancyBboxPatch((5.0, -0.3), 1.8, 4.8,
                            boxstyle="round,pad=0.15",
                            facecolor='#E67E22', edgecolor='#333',
                            linewidth=1.5, alpha=0.85, zorder=2)
    ax.add_patch(d_box)
    ax.text(5.9, 2.2, "D₂ₙ₋₁\n(Cyclic\nPerm.)", ha='center', va='center',
            fontsize=11, fontweight='bold', color='white', zorder=3)
    ax.text(5.9, -0.7, "O(k) gates", ha='center', va='center',
            fontsize=8, color='#666', style='italic')

    # Block: Measurement
    for y in [5.5, 4.0, 2.5, 0.2]:
        meter = FancyBboxPatch((8.5, y - 0.35), 0.9, 0.7,
                                boxstyle="round,pad=0.05",
                                facecolor=COLORS['measure'], edgecolor='#333',
                                linewidth=1.2, alpha=0.9, zorder=2)
        ax.add_patch(meter)
        ax.text(8.95, y, "M", ha='center', va='center',
                fontsize=10, fontweight='bold', color='white', zorder=3)

    ax.text(8.95, 6.3, "Measurement", ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['measure'])

    # Post-selection box
    ps_box = FancyBboxPatch((10.2, 4.8), 2.2, 1.4,
                             boxstyle="round,pad=0.12",
                             facecolor=COLORS['post'], edgecolor='#333',
                             linewidth=1.5, alpha=0.9, zorder=2)
    ax.add_patch(ps_box)
    ax.text(11.3, 5.5, "Post-select\nAncilla = |1⟩", ha='center', va='center',
            fontsize=9, fontweight='bold', color='white', zorder=3)

    draw_arrow(ax, 9.4, 5.5, 10.2, 5.5)

    # Result
    res_box = FancyBboxPatch((10.2, 1.5), 2.2, 1.4,
                              boxstyle="round,pad=0.12",
                              facecolor=COLORS['output'], edgecolor='#333',
                              linewidth=1.5, alpha=0.9, zorder=2)
    ax.add_patch(res_box)
    ax.text(11.3, 2.2, "Edge\nProbabilities\n|cⱼ - cⱼ'|²", ha='center', va='center',
            fontsize=9, fontweight='bold', color='white', zorder=3)

    draw_arrow(ax, 11.3, 4.8, 11.3, 2.9)

    plt.tight_layout(pad=1.0)
    path = os.path.join(FIGURES_DIR, "qhed_circuit_blocks.svg")
    fig.savefig(path, format='svg', bbox_inches='tight', pad_inches=0.3)
    plt.close(fig)
    print(f"  [OK] {path}")
    return path


# ==========================================================================
# Figure 3: Comparison Table (Approaches)
# ==========================================================================
def generate_comparison_table():
    """기존 QED 접근들과의 비교표 (장점/한계/리소스)"""
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.axis('off')
    fig.patch.set_facecolor(COLORS['bg'])

    ax.text(0.5, 0.96, "Quantum Edge Detection Approaches — Comparison",
            ha='center', va='center', transform=ax.transAxes,
            fontsize=16, fontweight='bold', color='#1a1a2e')

    columns = [
        "Method", "Encoding", "Edge\nDefinition", "Circuit\nType",
        "Qubits\n(for 2ᵏ×2ᵏ)", "Detection\nComplexity",
        "Noise\nAware", "Hardware\nDemo", "Key Limitation"
    ]

    rows = [
        ["QHED\n(Yao 2017)", "Amplitude", "Gradient\n(1st deriv.)", "Hadamard\n+ D₂ₙ₋₁",
         "2k + 1", "O(k)", "Partial", "Yes\n(IBM 5Q)", "Encoding\ncost O(n²)"],
        ["NEQR Edge\n(Zhang 2013)", "Basis\n(NEQR)", "Gradient\n(comparator)", "Quantum\nComparator",
         "2n + q\n(~24 for 256²)", "O(n²)", "No", "No", "High qubit\ncount"],
        ["Q-Laplacian\n(Fan 2019)", "Amplitude\n/ FRQI", "Laplacian\n(2nd deriv.)", "Shift\nOperator",
         "2k + q + a", "O(n²)", "No", "No", "Noise\nsensitivity"],
        ["QHED-BR\n(This Work)", "Amplitude", "Gradient\n(1st deriv.)", "Hadamard\n+ D₂ₙ₋₁",
         "2k + 1", "O(k)", "Partial", "Yes\n(IBM Heron)", "Encoding\ncost O(n²)"],
        ["Classical\nSobel", "N/A", "Gradient\n(convolution)", "N/A",
         "N/A", "O(n²)", "N/A", "N/A", "Scales\nlinearly"],
        ["Classical\nCanny", "N/A", "Gradient\n+ NMS", "N/A",
         "N/A", "O(n²)", "N/A", "N/A", "Parameter\ntuning"],
    ]

    n_cols = len(columns)
    n_rows = len(rows)

    col_widths = [0.11, 0.09, 0.09, 0.09, 0.10, 0.10, 0.07, 0.09, 0.10]
    x_positions = [0.04]
    for w in col_widths[:-1]:
        x_positions.append(x_positions[-1] + w)

    row_height = 0.105
    header_y = 0.87
    start_y = header_y - row_height

    # Header
    for j, col in enumerate(columns):
        ax.text(x_positions[j] + col_widths[j]/2, header_y, col,
                ha='center', va='center', fontsize=8.5, fontweight='bold',
                color='white', transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#2C3E50',
                          edgecolor='#1a1a2e', alpha=0.95))

    # Separator
    ax.plot([0.03, 0.97], [header_y - row_height*0.45, header_y - row_height*0.45],
            color='#333', linewidth=1.5, transform=ax.transAxes, clip_on=False)

    # Rows
    row_colors = ['#E8F4FD', '#F5F0FF', '#FFF5E6', '#E8F8E8', '#F5F5F5', '#F5F5F5']
    for i, row in enumerate(rows):
        y = start_y - i * row_height
        # Row background
        rect = plt.Rectangle((0.03, y - row_height*0.42), 0.94, row_height*0.88,
                              transform=ax.transAxes, facecolor=row_colors[i],
                              edgecolor='#ddd', linewidth=0.5, alpha=0.7, zorder=0)
        ax.add_patch(rect)

        for j, cell in enumerate(row):
            weight = 'bold' if j == 0 else 'normal'
            color = '#1a1a2e' if j == 0 else '#333'
            ax.text(x_positions[j] + col_widths[j]/2, y, cell,
                    ha='center', va='center', fontsize=7.5,
                    fontweight=weight, color=color,
                    transform=ax.transAxes)

    # Legend note
    ax.text(0.5, 0.05,
            "Note: Detection complexity excludes encoding cost. "
            "n = total pixels, k = log₂(image side length), q = grayscale bits, a = ancilla qubits.",
            ha='center', va='center', fontsize=8, color='#666',
            style='italic', transform=ax.transAxes)

    plt.tight_layout(pad=1.0)
    path = os.path.join(FIGURES_DIR, "qed_comparison_table.svg")
    fig.savefig(path, format='svg', bbox_inches='tight', pad_inches=0.3)
    plt.close(fig)
    print(f"  [OK] {path}")
    return path


# ==========================================================================
# Main
# ==========================================================================
if __name__ == "__main__":
    print("Generating QED Research Archive Figures...")
    generate_pipeline_overview()
    generate_circuit_block_diagram()
    generate_comparison_table()
    print("\nAll figures generated successfully!")
