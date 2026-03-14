# Quantum Image Edge Detection Using Improved Sobel Mask Based on NEQR

> **Entry ID**: `chetia2021_improved_sobel`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Extends quantum Sobel edge detection from 2 directions to 4 directions (horizontal, vertical, and both diagonals)
- Uses NEQR encoding for deterministic pixel value recovery
- Incorporates non-maximum suppression (NMS) and double thresholding techniques from classical Canny
- Achieves computational complexity ~O(n² + q²) with exponential speedup over classical and prior quantum Sobel methods

---

## (B) Detailed Summary

### Problem Statement

Prior quantum Sobel algorithms (QSobel) only detect edges in horizontal and vertical directions, missing significant diagonal edge information. Can a 4-direction quantum Sobel with refined post-processing improve edge quality?

### Core Idea

Design quantum circuits for all four Sobel gradient masks (horizontal, vertical, +45°, -45°) operating on NEQR-encoded images. After gradient computation, apply quantum non-maximum suppression and double thresholding to produce thin, clean edges analogous to the classical Canny pipeline.

### Method

1. **NEQR encoding**: Encode image with deterministic basis-state pixel representation
2. **4-direction gradient**: Quantum circuits compute gradients in horizontal, vertical, and both diagonal directions simultaneously via quantum parallelism
3. **Non-maximum suppression**: Quantum comparator circuits thin edges by keeping only local gradient maxima
4. **Double thresholding**: Classify pixels as strong/weak/non-edge using quantum comparison against two thresholds

### Results

- Significantly better edge quality than 2-direction quantum Sobel
- Complexity ~O(n² + q²), providing exponential speedup vs. all classical and prior quantum Sobel methods
- Simulation demonstrates edge quality approaching classical Canny

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
|NEQR Image⟩ ─┬── [Gx circuit (horizontal)] ──┐
               ├── [Gy circuit (vertical)] ─────┤
               ├── [G+45 circuit (diagonal)] ───┤── [NMS] ── [Double Threshold] ── |Edge⟩
               └── [G-45 circuit (diagonal)] ───┘
```

### Key Equations

**4-direction Sobel masks**:

$$G_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad G_{+45} = \begin{bmatrix} 0 & 1 & 2 \\ -1 & 0 & 1 \\ -2 & -1 & 0 \end{bmatrix}$$

(with analogous masks for $G_y$ and $G_{-45}$)

**Complexity**: $O(n^2 + q^2)$ where $n$ = position qubits, $q$ = intensity qubits.

---

## (D) Strengths / Contributions

- First 4-direction quantum Sobel implementation with Canny-like post-processing
- NEQR encoding provides exact pixel values for accurate gradient computation
- Quantum NMS and double thresholding produce thin, high-quality edges
- Exponential speedup claimed over both classical and prior quantum Sobel methods

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | NEQR requires 2n+q qubits; encoding circuit is expensive |
| Qubit overhead | Additional ancilla qubits needed for NMS and thresholding |
| Noise sensitivity | Complex circuit with many gates; impractical on current NISQ devices |
| Scalability | Simulation only; hardware feasibility not demonstrated |
| Reproducibility | No public code repository |

---

## (F) Comparison / Baselines

| Method | Directions | Complexity | Edge Quality | NMS |
|--------|-----------|-----------|-------------|-----|
| This paper (4-dir Sobel) | 4 | O(n² + q²) | High | Yes |
| QSobel (Yi 2015) | 2 | O(n²) | Moderate | No |
| QHED (Yao 2017) | All (amplitude) | O(k) | Moderate | No |
| Classical Canny | All | O(n²) | High | Yes |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, NumPy |
| Dataset | Small grayscale test images |
| Qubit count | 2n + q + ancilla (significant overhead) |
| Circuit depth | O(n² + q²) |
| Execution environment | Simulator only |
| Runtime / cost | Simulation: moderate |
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
@article{chetia2021quantum,
  title   = {Quantum image edge detection using improved Sobel mask based on NEQR},
  author  = {Chetia, Rohit and Boruah, S. M. Borah and Sahu, Pranab Priyam},
  journal = {Quantum Information Processing},
  volume  = {20},
  number  = {1},
  pages   = {21},
  year    = {2021},
  doi     = {10.1007/s11128-020-02944-7},
}
```

**Link**: [https://doi.org/10.1007/s11128-020-02944-7](https://doi.org/10.1007/s11128-020-02944-7)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

![Comparison Table](../../figures/qed_comparison_table.svg)

---

## (K) Open Questions / Future Research Ideas

- Can the quantum NMS circuit be simplified for NISQ compatibility?
- How does 4-direction compare to 8-direction quantum Sobel quantitatively?
- Is there a way to combine NEQR's deterministic encoding with amplitude encoding's qubit efficiency?
