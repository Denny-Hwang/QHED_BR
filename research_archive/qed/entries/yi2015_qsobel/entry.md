# QSobel: A Novel Quantum Image Edge Extraction Algorithm

> **Entry ID**: `yi2015_qsobel`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- First quantum implementation of the classical Sobel operator for edge extraction
- Uses FRQI (Flexible Representation of Quantum Images) encoding with superposition to process all pixels simultaneously
- Achieves O(n²) computational complexity for a 2^n × 2^n FRQI image
- Pioneering work that spawned a family of improved quantum Sobel algorithms (4-dir, 8-dir)

---

## (B) Detailed Summary

### Problem Statement

The Sobel operator is one of the most widely used classical edge detectors. Can it be translated into a quantum circuit that leverages superposition to process all pixels in parallel?

### Core Idea

Since FRQI stores all pixel information in a superposition state, applying quantum operations corresponding to the Sobel gradient masks processes all pixels simultaneously. The algorithm computes horizontal and vertical gradients via quantum shift and controlled-rotation operations, then combines them to produce an edge map.

### Method

1. **FRQI encoding**: Represent the image as $|I\rangle = \frac{1}{2^n}\sum_{i=0}^{2^{2n}-1}(\cos\theta_i|0\rangle + \sin\theta_i|1\rangle)|i\rangle$
2. **Gradient computation**: Apply quantum circuits implementing horizontal ($G_x$) and vertical ($G_y$) Sobel masks using controlled rotations and cyclic shifts on position qubits
3. **Magnitude estimation**: Combine $G_x$ and $G_y$ to approximate gradient magnitude $G = \sqrt{G_x^2 + G_y^2}$
4. **Measurement**: Measure to obtain the edge-enhanced image

### Results

- Successfully extracts edges using quantum Sobel operator in simulation
- Complexity O(n²) for 2^n × 2^n FRQI image
- Limited to horizontal and vertical directions (2-direction Sobel)
- Cannot accurately measure color information due to FRQI's probabilistic encoding

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
|FRQI Image⟩ ─── [Shift X ±1] ─── [Controlled Rotation (Gx weights)] ─── |Gx⟩
|FRQI Image⟩ ─── [Shift Y ±1] ─── [Controlled Rotation (Gy weights)] ─── |Gy⟩
|Gx⟩, |Gy⟩ ─── [Combine] ─── [Measure] ─── Edge Map
```

### Key Equations

**Classical Sobel masks**:

$$G_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$

**Gradient magnitude**: $G = \sqrt{G_x^2 + G_y^2} \approx |G_x| + |G_y|$

---

## (D) Strengths / Contributions

- First quantum realization of the widely-used Sobel operator
- Demonstrates that classical convolution-based detectors can be mapped to quantum circuits
- Exploits FRQI superposition for parallel pixel processing
- Foundation for subsequent improved quantum Sobel algorithms

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | FRQI encoding requires O(2^{2n}) gates |
| Direction limitation | Only 2 directions (horizontal, vertical); misses diagonal edges |
| Intensity accuracy | FRQI's probabilistic encoding prevents accurate color/intensity measurement |
| Scalability | Simulation only; no hardware demonstration |
| Reproducibility | No public code |

---

## (F) Comparison / Baselines

| Method | Directions | Encoding | Complexity | Intensity Accuracy |
|--------|-----------|----------|------------|-------------------|
| QSobel (this paper) | 2 | FRQI | O(n²) | Probabilistic |
| Classical Sobel | 2 | N/A | O(n²) | Exact |
| QHED (Yao 2017) | All (amplitude diff) | Amplitude | O(k) detection | Probabilistic |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, NumPy |
| Dataset | Small grayscale images |
| Qubit count | 2n + 1 (FRQI) + ancilla |
| Circuit depth | O(n²) |
| Execution environment | Simulator |
| Runtime / cost | Simulation: seconds for small images |
| Code availability | Not publicly available |

---

## (H) Keywords / Tags

- **Data encoding**: FRQI
- **Edge definition**: gradient
- **Circuit type**: shift_operator
- **Noise-aware**: no
- **Evaluation**: visual, complexity

---

## (I) Citation

```bibtex
@article{yi2015qsobel,
  title   = {QSobel: A novel quantum image edge extraction algorithm},
  author  = {Yi, Zhang and Kai, Lu and Yinghui, Gao},
  journal = {Science China Information Sciences},
  volume  = {58},
  number  = {1},
  pages   = {1--13},
  year    = {2015},
  doi     = {10.1007/s11432-014-5158-9},
}
```

**Link**: [https://doi.org/10.1007/s11432-014-5158-9](https://doi.org/10.1007/s11432-014-5158-9)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

---

## (K) Open Questions / Future Research Ideas

- Can extending to 4 or 8 directions significantly improve edge quality? (Answered by later works)
- How to handle FRQI's probabilistic intensity encoding for accurate gradient computation?
- Is a quantum Scharr operator (improved Sobel) feasible?
