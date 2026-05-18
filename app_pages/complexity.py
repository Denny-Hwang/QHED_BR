"""Page 4 — Computational Complexity Comparison."""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def render() -> None:
    st.title("Computational Complexity: QHED-BR vs Classical")

    st.header("1. Notation and Definitions")
    st.markdown(
        "We compare QHED-BR against classical edge detection. "
        "All comparisons use **Boundary Restoration (BR)** since it is essential for correct results."
    )
    st.markdown("""
| Symbol | Definition |
|--------|-----------|
| $N$ | Image side length ($N \\times N$ image) |
| $p = 2^k$ | Patch side length ($p \\times p$ patch) |
| $k$ | Qubits per spatial dimension ($k \\geq 3$, minimum 8x8 patches) |
| $q = 2k + 1$ | Total qubits per QHED circuit ($2k$ data + 1 ancilla) |
| $Q$ | Number of patches with BR |
| $\\alpha$ | Hardware speed ratio = (time per quantum gate) / (time per classical op) |
""")
    st.markdown("**Patch count with BR** (stride $= p - 2$, 2-pixel overlap for boundary zeroing):")
    st.latex(r"Q_{\text{BR}} = \left\lceil \frac{N - 2}{p - 2} \right\rceil^2 \approx \frac{N^2}{(p-2)^2} \;\;\text{for}\; N \gg p")

    st.header("2. QHED: Per-Patch Operation Breakdown")
    st.markdown(
        "Each QHED patch passes through three stages. "
        "The cost of each stage determines whether quantum processing beats classical."
    )

    st.subheader("Stage 1: Amplitude Encoding (Classical -> Quantum)")
    st.markdown("The $p^2$ pixel values are encoded into quantum state amplitudes:")
    st.latex(r"|\psi\rangle = \sum_{i=0}^{p^2 - 1} a_i |i\rangle, \quad \sum |a_i|^2 = 1")
    st.markdown(
        "Arbitrary state preparation on $m$ qubits requires $O(2^m)$ CNOT gates "
        "(Shende, Bullock & Markov, 2006). For $m = 2k$ data qubits, run twice for H/V scans:"
    )
    st.latex(r"G_{\text{encode}} = 2 \times O(2^{2k}) = 2p^2 \;\text{quantum gates per patch}")

    st.subheader("Stage 2: Quantum Edge Detection")
    st.markdown("The detection circuit: $H \\to D_{2n-1} \\to H$ on $q = 2k+1$ qubits.")
    st.markdown(
        "The permutation unitary $D_{2n-1}$ maps $|x\\rangle \\to |x + 1 \\bmod 2^q\\rangle$. "
        "This is a **quantum increment circuit**, decomposable into $O(q)$ Toffoli gates "
        "(Takahashi & Kunihiro, 2005). Using $c_D \\approx 10$ elementary gates per qubit "
        "as a practical estimate (accounting for Toffoli decomposition):"
    )
    st.latex(r"G_{\text{detect}} = 2 \times c_D \cdot q = 2 c_D (2k+1) \approx 40k \;\text{quantum gates per patch}")
    st.markdown(
        "**This is where quantum parallelism shines**: a single circuit of $O(k)$ gates "
        "computes all $p^2 = 2^{2k}$ pixel differences simultaneously. "
        "A classical method needs $O(p^2)$ operations for the same pixels."
    )

    st.subheader("Stage 3: Readout (Quantum -> Classical)")
    st.markdown(
        "Extract $p^2$ amplitudes from the statevector and threshold for edges. "
        "Two scan directions, each requiring extraction + threshold:"
    )
    st.latex(r"C_{\text{readout}} = 4p^2 \;\text{classical ops per patch}")

    st.markdown("---")
    st.markdown("**Summary per patch:**")
    st.markdown("""
| Stage | Count | Type |
|-------|-------|------|
| Encoding | $2p^2$ | Quantum gates |
| Detection | $\\sim 40k$ | Quantum gates |
| Readout | $4p^2$ | Classical ops |
| **Quantum total** | $\\mathbf{2p^2 + 40k}$ | **Quantum gates** |
| **Classical total** | $\\mathbf{4p^2}$ | **Classical ops** |
""")

    st.header("3. Classical Edge Detection Complexity")
    st.markdown("""
| Method | Kernel | Ops/pixel | Total |
|--------|--------|-----------|-------|
| **Sobel** | Two $3 \\times 3$ kernels ($G_x, G_y$) | $\\sim 2 \\times 17 + 3 \\approx 37$ | $37 N^2$ |
| **Prewitt** | Two $3 \\times 3$ kernels | $\\sim 37$ | $37 N^2$ |
| **Laplacian** | One $3 \\times 3$ kernel | $\\sim 17$ | $17 N^2$ |
| **Canny** | Blur + gradient + NMS + hysteresis | $\\sim 100$ | $100 N^2$ |
""")
    st.markdown("All methods:")
    st.latex(r"T_{\text{classical}} = c_{\text{cl}} \cdot N^2 \;\;\text{classical operations}")
    st.markdown("where $c_{\\text{cl}} \\approx 37$ for Sobel and $c_{\\text{cl}} \\approx 100$ for Canny.")

    st.header("4. Case 1: Detection Only (Excluding Encoding/Decoding)")
    st.markdown(
        "If quantum data is **already loaded** (e.g., via QRAM or native quantum sensors), "
        "we isolate the pure quantum detection advantage."
    )

    st.markdown("**Total quantum detection gates for full image:**")
    st.latex(r"G_{\text{detect}}^{\text{total}} = Q_{\text{BR}} \times 40k = \frac{40k \cdot N^2}{(p-2)^2}")
    st.markdown("**Total execution time** with hardware speed ratio $\\alpha$:")
    st.latex(r"T_{\text{QHED}}^{(\text{det})} = \alpha \cdot \frac{40k \cdot N^2}{(p-2)^2}")
    st.latex(r"T_{\text{classical}} = c_{\text{cl}} \cdot N^2")
    st.markdown("**Quantum wins** when $T_{\\text{QHED}}^{(\\text{det})} < T_{\\text{classical}}$:")
    st.latex(r"\alpha < \frac{c_{\text{cl}} \cdot (p-2)^2}{40k} \;\; \stackrel{\text{def}}{=} \;\; \alpha_{\max}^{(\text{det})}")

    c_D_const = 10
    det_gate_factor = 2 * 2 * c_D_const

    st.markdown("**Crossover table (detection only):**")
    det_rows = []
    for k_val in [3, 4, 5, 6, 7]:
        p_val = 2 ** k_val
        alpha_sobel = 37 * (p_val - 2) ** 2 / (det_gate_factor * k_val)
        alpha_canny = 100 * (p_val - 2) ** 2 / (det_gate_factor * k_val)
        det_rows.append(
            f"| {k_val} | {p_val} | {37*(p_val-2)**2:,} | {det_gate_factor*k_val} | "
            f"**{alpha_sobel:.1f}** | **{alpha_canny:.1f}** |"
        )
    st.markdown(
        "| $k$ | $p$ | $c_{\\text{cl}}(p-2)^2$ (Sobel) | $40k$ | "
        "$\\alpha_{\\max}$ vs Sobel | $\\alpha_{\\max}$ vs Canny |\n"
        "|-----|-----|---:|---:|---:|---:|\n" + "\n".join(det_rows)
    )
    st.markdown(
        "Even with $\\alpha = 100$ (current NISQ estimate), quantum detection beats Canny for $k \\geq 4$ "
        "and beats Sobel for $k \\geq 5$. "
        "At $\\alpha = 10$ (near-term target), quantum beats Sobel for all $k \\geq 3$."
    )

    st.subheader("Case 1 Visualization")
    sizes = np.array([2 ** i for i in range(4, 12)])

    fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(14, 5.5))
    for k in [3, 4, 5, 6]:
        p = 2 ** k
        stride = max(p - 2, 1)
        Q_br = np.array([int(np.ceil((s - 2) / stride)) ** 2 if s >= p else 1 for s in sizes])
        ops = Q_br * det_gate_factor * k
        ax1a.plot(sizes, ops, "o-", label=f"QHED k={k} (p={p})", linewidth=2, markersize=5)
    ax1a.plot(sizes, 37 * sizes ** 2, "k^--", label="Sobel (37 ops/px)", linewidth=2.5, markersize=7)
    ax1a.plot(sizes, 100 * sizes ** 2, "ks--", label="Canny (100 ops/px)", linewidth=2, markersize=5, alpha=0.6)
    ax1a.set_xlabel("Image side length N", fontsize=12)
    ax1a.set_ylabel("Total operations", fontsize=12)
    ax1a.set_title(r"Detection Only ($\alpha=1$)", fontsize=13)
    ax1a.set_yscale("log"); ax1a.set_xscale("log", base=2)
    ax1a.legend(fontsize=8); ax1a.grid(True, alpha=0.3)

    k_arr = np.arange(3, 9)
    p_arr = 2.0 ** k_arr
    alpha_max_sobel = 37 * (p_arr - 2) ** 2 / (det_gate_factor * k_arr)
    alpha_max_canny = 100 * (p_arr - 2) ** 2 / (det_gate_factor * k_arr)
    x_pos = np.arange(len(k_arr))
    width = 0.35
    ax1b.bar(x_pos - width / 2, alpha_max_sobel, width, label="vs Sobel", color="#2196F3", edgecolor="black", linewidth=0.5)
    ax1b.bar(x_pos + width / 2, alpha_max_canny, width, label="vs Canny", color="#FF9800", edgecolor="black", linewidth=0.5)
    ax1b.axhline(y=100, color="red", linestyle="--", linewidth=1.5, label=r"Current NISQ $\alpha \approx 100$")
    ax1b.axhline(y=10, color="green", linestyle=":", linewidth=1.5, label=r"Near-term $\alpha \approx 10$")
    for i, (as_, ac_) in enumerate(zip(alpha_max_sobel, alpha_max_canny)):
        ax1b.text(i - width / 2, as_ * 1.1, f"{as_:.0f}", ha="center", fontsize=8, fontweight="bold")
        ax1b.text(i + width / 2, ac_ * 1.1, f"{ac_:.0f}", ha="center", fontsize=8, fontweight="bold")
    ax1b.set_xlabel("k (qubits per dimension)", fontsize=12)
    ax1b.set_ylabel(r"Max $\alpha$ for quantum advantage", fontsize=12)
    ax1b.set_title("Detection-Only: Crossover Threshold", fontsize=13)
    ax1b.set_xticks(x_pos)
    ax1b.set_xticklabels([f"k={k}\np={2**k}" for k in k_arr], fontsize=9)
    ax1b.set_yscale("log"); ax1b.legend(fontsize=8); ax1b.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.header("5. Case 2: End-to-End (Including Encoding & Decoding)")
    st.markdown(
        "In practice, classical image data must be encoded into quantum states "
        "and results read out. This is the honest comparison for current systems."
    )
    st.markdown("**Total execution time** (quantum + classical readout):")
    st.latex(r"T_{\text{QHED}}^{(\text{e2e})} = \underbrace{\alpha \cdot Q_{\text{BR}} \cdot (2p^2 + 40k)}_{\text{quantum gates}} \;+\; \underbrace{Q_{\text{BR}} \cdot 4p^2}_{\text{classical readout}}")
    st.markdown("**Quantum wins** when $T_{\\text{QHED}}^{(\\text{e2e})} < T_{\\text{classical}} = c_{\\text{cl}} N^2$:")
    st.latex(r"\alpha \cdot \frac{2p^2 + 40k}{(p-2)^2} + \frac{4p^2}{(p-2)^2} < c_{\text{cl}}")
    st.markdown("Solving for the maximum tolerable hardware speed ratio:")
    st.latex(r"\alpha_{\max}^{(\text{e2e})} = \frac{c_{\text{cl}}(p-2)^2 - 4p^2}{2p^2 + 40k}")

    st.markdown("**Crossover table (end-to-end):**")
    e2e_rows = []
    for k_val in [3, 4, 5, 6, 7]:
        p_val = 2 ** k_val
        readout_term = 4 * p_val ** 2 / (p_val - 2) ** 2
        alpha_sobel = (37 * (p_val - 2) ** 2 - 4 * p_val ** 2) / (2 * p_val ** 2 + det_gate_factor * k_val)
        alpha_canny = (100 * (p_val - 2) ** 2 - 4 * p_val ** 2) / (2 * p_val ** 2 + det_gate_factor * k_val)
        e2e_rows.append(f"| {k_val} | {p_val} | {readout_term:.2f} | **{alpha_sobel:.1f}** | **{alpha_canny:.1f}** |")
    st.markdown(
        "| $k$ | $p$ | Readout overhead $4p^2/(p-2)^2$ | "
        "$\\alpha_{\\max}$ vs Sobel | $\\alpha_{\\max}$ vs Canny |\n"
        "|-----|-----|---:|---:|---:|\n" + "\n".join(e2e_rows)
    )

    st.markdown("""
**Key insight:** With encoding included, both QHED-BR and classical are $O(N^2)$.
The crossover depends entirely on the hardware constant $\\alpha$:

- **Current NISQ** ($\\alpha \\approx 100$--$10{,}000$): Classical wins for all $k$.
  Encoding $2p^2$ quantum gates per patch dominates, and each gate is slow.
- **Near-term** ($\\alpha \\approx 10$): Quantum competitive vs Canny for $k \\geq 4$.
- **Fault-tolerant** ($\\alpha \\approx 1$): Quantum wins for all $k \\geq 3$.
- **With QRAM** ($O(\\log p^2)$ encoding): Eliminates the encoding bottleneck,
  recovering Case 1's advantage even end-to-end.
""")

    st.subheader("Case 2 Visualization")
    fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 5.5))
    for k in [3, 4, 5, 6]:
        p = 2 ** k
        stride = max(p - 2, 1)
        Q_br = np.array([int(np.ceil((s - 2) / stride)) ** 2 if s >= p else 1 for s in sizes])
        ops = Q_br * (2 * p ** 2 + det_gate_factor * k) + Q_br * 4 * p ** 2
        ax2a.plot(sizes, ops, "o-", label=f"QHED k={k} (p={p})", linewidth=2, markersize=5)
    ax2a.plot(sizes, 37 * sizes ** 2, "k^--", label="Sobel (37 ops/px)", linewidth=2.5, markersize=7)
    ax2a.plot(sizes, 100 * sizes ** 2, "ks--", label="Canny (100 ops/px)", linewidth=2, markersize=5, alpha=0.6)
    ax2a.set_xlabel("Image side length N", fontsize=12)
    ax2a.set_ylabel("Total operations", fontsize=12)
    ax2a.set_title(r"End-to-End ($\alpha=1$, optimistic)", fontsize=13)
    ax2a.set_yscale("log"); ax2a.set_xscale("log", base=2)
    ax2a.legend(fontsize=8); ax2a.grid(True, alpha=0.3)

    alpha_e2e_sobel = np.array([
        (37 * (2 ** k - 2) ** 2 - 4 * 4 ** k) / (2 * 4 ** k + det_gate_factor * k)
        for k in k_arr
    ])
    alpha_e2e_canny = np.array([
        (100 * (2 ** k - 2) ** 2 - 4 * 4 ** k) / (2 * 4 ** k + det_gate_factor * k)
        for k in k_arr
    ])
    ax2b.bar(x_pos - width / 2, alpha_e2e_sobel, width, label="vs Sobel", color="#2196F3", edgecolor="black", linewidth=0.5)
    ax2b.bar(x_pos + width / 2, alpha_e2e_canny, width, label="vs Canny", color="#FF9800", edgecolor="black", linewidth=0.5)
    ax2b.axhline(y=10, color="green", linestyle=":", linewidth=1.5, label=r"Near-term $\alpha \approx 10$")
    ax2b.axhline(y=1, color="red", linestyle="--", linewidth=1.5, label=r"Fault-tolerant $\alpha \approx 1$")
    for i, (as_, ac_) in enumerate(zip(alpha_e2e_sobel, alpha_e2e_canny)):
        ax2b.text(i - width / 2, as_ + 0.3, f"{as_:.1f}", ha="center", fontsize=8, fontweight="bold")
        ax2b.text(i + width / 2, ac_ + 0.3, f"{ac_:.1f}", ha="center", fontsize=8, fontweight="bold")
    ax2b.set_xlabel("k (qubits per dimension)", fontsize=12)
    ax2b.set_ylabel(r"Max $\alpha$ for quantum advantage", fontsize=12)
    ax2b.set_title("End-to-End: Crossover Threshold", fontsize=13)
    ax2b.set_xticks(x_pos)
    ax2b.set_xticklabels([f"k={k}\np={2**k}" for k in k_arr], fontsize=9)
    ax2b.legend(fontsize=8); ax2b.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.header("6. Space Complexity: Exponential Memory Advantage")
    st.markdown(
        "Regardless of time overhead, QHED achieves an **exponential advantage in space**. "
        "This is the most unambiguous quantum advantage:"
    )
    st.latex(r"\text{Classical: } O(p^2) = O(2^{2k}) \text{ memory cells per patch}")
    st.latex(r"\text{Quantum: } O(q) = O(2k+1) \text{ qubits per patch}")
    st.latex(r"\text{Compression ratio} = \frac{2^{2k}}{2k+1} \;\xrightarrow{k \to \infty}\; \text{exponential}")

    st.markdown("""
| Patch | Pixels | Classical | Quantum | Compression |
|-------|--------|-----------|---------|-------------|
| $8 \\times 8$ | 64 | 64 values | **7** qubits | 9.1x |
| $16 \\times 16$ | 256 | 256 values | **9** qubits | 28.4x |
| $32 \\times 32$ | 1024 | 1024 values | **11** qubits | 93.1x |
| $64 \\times 64$ | 4096 | 4096 values | **13** qubits | 315.1x |
| $128 \\times 128$ | 16384 | 16384 values | **15** qubits | 1092.3x |
| $256 \\times 256$ | 65536 | 65536 values | **17** qubits | 3855.1x |
""")

    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 5.5))
    k_vals = np.arange(3, 10)
    p_vals = 2 ** k_vals
    classical_mem = p_vals ** 2
    quantum_mem = 2 * k_vals + 1
    compression = classical_mem / quantum_mem
    ax3a.semilogy(k_vals, classical_mem, "ro-", label=r"Classical: $p^2 = 2^{2k}$", linewidth=2.5, markersize=8)
    ax3a.semilogy(k_vals, quantum_mem, "bs-", label=r"Quantum: $2k+1$", linewidth=2.5, markersize=8)
    ax3a.fill_between(k_vals, quantum_mem, classical_mem, alpha=0.15, color="green", label="Exponential gap")
    ax3a.set_xlabel("k (qubits per dimension)", fontsize=12)
    ax3a.set_ylabel("Memory units", fontsize=12)
    ax3a.set_title("Space: Classical vs Quantum", fontsize=13)
    ax3a.legend(fontsize=10); ax3a.grid(True, alpha=0.3)
    ax3a.set_xticks(k_vals)
    ax3a.set_xticklabels([f"{k}\n({2**k}x{2**k})" for k in k_vals], fontsize=8)

    ax3b.bar(k_vals, compression, color="#4CAF50", edgecolor="black", linewidth=0.5)
    for ki, cr in zip(k_vals, compression):
        ax3b.text(ki, cr * 1.1, f"{cr:.0f}x", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax3b.set_xlabel("k (qubits per dimension)", fontsize=12)
    ax3b.set_ylabel(r"Compression ratio ($p^2 / (2k+1)$)", fontsize=12)
    ax3b.set_title("Memory Compression Ratio", fontsize=13)
    ax3b.set_yscale("log"); ax3b.grid(True, alpha=0.3, axis="y")
    ax3b.set_xticks(k_vals)
    ax3b.set_xticklabels([f"k={k}\np={2**k}" for k in k_vals], fontsize=8)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.header("7. BR Overhead: Patch Count Analysis")
    st.markdown("BR increases patch count by a polynomial factor that vanishes for large $p$:")
    st.latex(r"\frac{Q_{\text{BR}}}{Q_{\text{no-BR}}} = \left(\frac{p}{p-2}\right)^2 \;\xrightarrow{p \to \infty}\; 1")

    col1, col2 = st.columns(2)
    sizes_plot = [2 ** i for i in range(4, 11)]

    with col1:
        fig4a, ax4a = plt.subplots(figsize=(8, 5))
        for qb in [3, 4, 5, 6]:
            patch = 2 ** qb
            br_stride = max(patch - 2, 1)
            patches_br = [int(np.ceil((s - 2) / br_stride)) ** 2 if s >= patch else 1 for s in sizes_plot]
            ax4a.plot(sizes_plot, patches_br, "o-", label=f"k={qb} ({patch}x{patch})", linewidth=2)
        ax4a.set_xlabel("Image side length N", fontsize=12)
        ax4a.set_ylabel("Number of patches (Q)", fontsize=12)
        ax4a.set_title("Patches Required with BR", fontsize=13)
        ax4a.legend(fontsize=10); ax4a.set_yscale("log"); ax4a.set_xscale("log", base=2)
        ax4a.grid(True, alpha=0.3)
        st.pyplot(fig4a)
        plt.close(fig4a)

    with col2:
        fig4b, ax4b = plt.subplots(figsize=(8, 5))
        k_overhead = np.arange(3, 9)
        p_overhead = 2.0 ** k_overhead
        overhead_ratio = (p_overhead / (p_overhead - 2)) ** 2
        colors_oh = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#00BCD4"]
        ax4b.bar(k_overhead, overhead_ratio, color=colors_oh, edgecolor="black", linewidth=0.5)
        ax4b.axhline(y=1.0, color="gray", linestyle="--", linewidth=1.5, label="No overhead (1.0x)")
        for ki, oh in zip(k_overhead, overhead_ratio):
            ax4b.text(ki, oh + 0.02, f"{oh:.2f}x", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax4b.set_xlabel("k (qubits per dimension)", fontsize=12)
        ax4b.set_ylabel(r"Patch overhead ratio $(p/(p-2))^2$", fontsize=12)
        ax4b.set_title("BR Overhead (converges to 1.0)", fontsize=13)
        ax4b.set_xticks(k_overhead)
        ax4b.set_xticklabels([f"k={k}\np={2**k}" for k in k_overhead], fontsize=9)
        ax4b.legend(fontsize=10); ax4b.grid(True, alpha=0.3, axis="y")
        ax4b.set_ylim(0.9, max(overhead_ratio) + 0.15)
        st.pyplot(fig4b)
        plt.close(fig4b)

    st.header("8. Combined Crossover: Three Regimes")
    st.markdown("The following plot shows all three operation regimes for a representative case ($k=4$, $p=16$):")

    fig5, ax5 = plt.subplots(figsize=(12, 6))
    N_range = np.logspace(np.log10(16), np.log10(4096), 200)
    k_ex, p_ex = 4, 16
    stride_ex = p_ex - 2
    Q_ex = np.ceil((N_range - 2) / stride_ex) ** 2
    detect_ops = Q_ex * det_gate_factor * k_ex
    e2e_alpha1 = Q_ex * (2 * p_ex ** 2 + det_gate_factor * k_ex) + Q_ex * 4 * p_ex ** 2
    e2e_alpha10 = 10 * Q_ex * (2 * p_ex ** 2 + det_gate_factor * k_ex) + Q_ex * 4 * p_ex ** 2
    e2e_alpha100 = 100 * Q_ex * (2 * p_ex ** 2 + det_gate_factor * k_ex) + Q_ex * 4 * p_ex ** 2
    sobel_ops = 37 * N_range ** 2
    canny_ops = 100 * N_range ** 2
    ax5.loglog(N_range, sobel_ops, "k-", label="Sobel (37 ops/px)", linewidth=2.5)
    ax5.loglog(N_range, canny_ops, "k--", label="Canny (100 ops/px)", linewidth=2, alpha=0.7)
    ax5.loglog(N_range, detect_ops, "b-", label=r"QHED detect only ($\alpha$=1)", linewidth=2)
    ax5.loglog(N_range, e2e_alpha1, "g-", label=r"QHED e2e $\alpha$=1 (fault-tol.)", linewidth=2)
    ax5.loglog(N_range, e2e_alpha10, "r--", label=r"QHED e2e $\alpha$=10 (near-term)", linewidth=2)
    ax5.loglog(N_range, e2e_alpha100, "r:", label=r"QHED e2e $\alpha$=100 (NISQ)", linewidth=2, alpha=0.7)
    ax5.fill_between(N_range, detect_ops, sobel_ops, alpha=0.06, color="blue")
    ax5.annotate(r"Quantum advantage zone (detection only)", xy=(200, 3e4), fontsize=10, color="blue", alpha=0.8)
    ax5.set_xlabel("Image side length N", fontsize=13)
    ax5.set_ylabel("Total equivalent operations", fontsize=13)
    ax5.set_title(f"Three Regimes: QHED-BR (k={k_ex}, p={p_ex}) vs Classical", fontsize=14)
    ax5.legend(fontsize=9, loc="upper left"); ax5.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

    st.header("9. Summary and Conclusions")
    st.markdown("**Advantage comparison:**")
    st.markdown("""
| Dimension | Classical | QHED-BR | Winner |
|-----------|----------|---------|--------|
| **Time (detection only)** | $c_{\\text{cl}} \\cdot N^2$ | $\\frac{40k \\cdot N^2}{(p-2)^2}$ | Quantum: speedup $\\propto p^2/k$ |
| **Time (end-to-end)** | $c_{\\text{cl}} \\cdot N^2$ | $\\sim \\frac{6p^2 \\cdot N^2}{(p-2)^2}$ | **Same** $O(N^2)$: depends on $\\alpha$ |
| **Space** | $O(p^2)$ per patch | $O(k)$ qubits | Quantum: **exponential** |
| **BR overhead** | -- | $(p/(p-2))^2 \\to 1$ | Polynomial, vanishes |
""")

    st.markdown("**Honest assessment:**")
    st.markdown("""
1. **Detection only**: QHED has a genuine, provable advantage of
   $\\Theta(p^2/k)$ fewer operations. This is significant -- at $k=5$ ($p=32$),
   the speedup exceeds 100x even accounting for hardware penalty.

2. **End-to-end**: The $O(p^2)$ encoding cost neutralizes the detection advantage.
   Both methods are $O(N^2)$, and the winner depends on hardware speed $\\alpha$.
   - $\\alpha < 4$: quantum wins vs Sobel for $k \\geq 3$
   - $\\alpha < 10$: quantum wins vs Canny for $k \\geq 3$
   - $\\alpha > 15$: classical wins for all $k$ vs Sobel

3. **Space**: The exponential compression ($2^{2k} \\to 2k+1$) is hardware-independent
   and represents the clearest quantum advantage of QHED-BR.

4. **NISQ reality**: Current quantum gates are ~$100$--$10{,}000\\times$ slower than
   classical FLOPs. End-to-end, classical methods are currently faster.
   However, QHED-BR circuits are **shallow** ($O(k)$ depth), making them
   among the most NISQ-friendly quantum algorithms.
""")

    st.markdown("---")
    st.markdown("""
**References:**
- Shende, Bullock & Markov, "Synthesis of quantum logic circuits," IEEE Trans. CAD, 2006
- Takahashi & Kunihiro, "A linear-size quantum circuit for addition with no ancillary qubits," Quantum Inf. Comput. 5(6), 2005
- Cuccaro et al., "A new quantum ripple-carry addition circuit," arXiv:quant-ph/0410184, 2004
- Yao et al., "Quantum image processing and its application to edge detection," Physical Review X 7.3, 2017
- [Qiskit](https://qiskit.org/) | [IBM Quantum](https://quantum-computing.ibm.com/)
""")
