# Quantum Image Edge Detection Based on Eight-Direction Sobel Operator for NEQR

> **Entry ID**: `ma2022_eight_direction_sobel`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Proposes the first 8-direction quantum Sobel edge detection algorithm for NEQR images
- Designs quantum circuits that simultaneously compute gradient values in all 8 compass directions
- Achieves finer edge detail preservation than 2-direction and 4-direction quantum Sobel methods
- Classifies pixels by comparing gradient magnitudes across all 8 directions

---

## (B) Detailed Summary

### Problem Statement

Existing quantum Sobel edge detection algorithms use only 2 or 4 directional gradient masks, leading to loss of edge detail in high-resolution images. Can extending to 8 directions capture finer edge information?

### Core Idea

Design 8 distinct Sobel-like gradient masks (N, NE, E, SE, S, SW, W, NW) and implement them as quantum circuits operating on NEQR-encoded images. Using quantum parallelism, all 8 gradient computations are performed simultaneously for every pixel.

### Method

1. **NEQR encoding**: Deterministic basis-state representation of pixel intensities
2. **8-direction gradient circuits**: Quantum circuits compute gradient values in all 8 compass directions (N, NE, E, SE, S, SW, W, NW) using shift and comparison operations
3. **Gradient classification**: Compare gradient magnitudes across directions to determine edge orientation and strength
4. **Edge map construction**: Pixels exceeding the gradient threshold are classified as edges

### Results

- Captures edge details missed by 2-dir and 4-dir methods, especially in images with complex textures
- Circuit complexity analysis confirms feasibility in simulation
- Simulation experiments on standard test images verify improved edge quality
- No hardware experiments

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
                    ┌── [G_N (North)] ──────┐
                    ├── [G_NE (Northeast)] ──┤
                    ├── [G_E (East)] ────────┤
|NEQR Image⟩ ──────┼── [G_SE (Southeast)] ──┼── [Max Gradient] ── [Threshold] ── |Edge⟩
                    ├── [G_S (South)] ───────┤
                    ├── [G_SW (Southwest)] ──┤
                    ├── [G_W (West)] ────────┤
                    └── [G_NW (Northwest)] ──┘
```

### Key Equations

**8-direction Sobel masks** (examples for N and NE):

$$G_N = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}, \quad G_{NE} = \begin{bmatrix} -2 & -1 & 0 \\ -1 & 0 & 1 \\ 0 & 1 & 2 \end{bmatrix}$$

**Edge criterion**: $\max(|G_N|, |G_{NE}|, \ldots, |G_{NW}|) > T$

---

## (D) Strengths / Contributions

- Most comprehensive directional quantum Sobel implementation (8 directions)
- Preserves fine edge details that 2-dir and 4-dir methods miss
- Quantum parallelism computes all 8 directions simultaneously
- Provides a thorough circuit complexity analysis

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | NEQR encoding requires 2n+q qubits with expensive initialization |
| Circuit complexity | 8-direction computation requires significantly more gates than 2-dir or 4-dir |
| Qubit overhead | Additional ancilla qubits needed for comparison and classification |
| Noise sensitivity | Deep circuits are highly vulnerable to noise on NISQ hardware |
| Reproducibility | Simulation only; no public code |

---

## (F) Comparison / Baselines

| Method | Directions | Edge Detail | Circuit Depth | Hardware Demo |
|--------|-----------|-------------|--------------|---------------|
| This paper (8-dir) | 8 | High | High | No |
| Chetia 2021 (4-dir) | 4 | Medium-High | Medium | No |
| QSobel (2-dir) | 2 | Medium | Low | No |
| QHED (Yao 2017) | All (amplitude) | Medium | Low | Yes |
| Classical Sobel | 2 (or 8 with variants) | Variable | O(n²) | N/A |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, NumPy, Matplotlib |
| Dataset | Standard test images (Lena, cameraman, etc.) |
| Qubit count | 2n + q + multiple ancilla |
| Circuit depth | Significantly deeper than 2-dir or 4-dir Sobel |
| Execution environment | Simulator only |
| Runtime / cost | Simulation: slower due to 8 gradient circuits |
| Code availability | Not publicly available |

---

## (H) Keywords / Tags

- **Data encoding**: NEQR
- **Edge definition**: gradient
- **Circuit type**: comparator
- **Noise-aware**: no
- **Evaluation**: visual, complexity

---

## (I) Citation

```bibtex
@article{ma2022quantum,
  title   = {Quantum image edge detection based on eight-direction Sobel operator for NEQR},
  author  = {Ma, Yining and Ma, Hongyang and Chu, Pengcheng},
  journal = {Quantum Information Processing},
  volume  = {21},
  pages   = {190},
  year    = {2022},
  doi     = {10.1007/s11128-022-03535-6},
}
```

**Link**: [https://doi.org/10.1007/s11128-022-03535-6](https://doi.org/10.1007/s11128-022-03535-6)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

![Comparison Table](../../figures/qed_comparison_table.svg)

---

## (K) Open Questions / Future Research Ideas

- Is 8-direction sufficient, or would a continuous orientation approach (e.g., steerable filters) offer further improvement?
- Can circuit depth be reduced through approximate gradient computation?
- How to make the 8-direction circuit NISQ-compatible?
