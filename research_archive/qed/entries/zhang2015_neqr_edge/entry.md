# NEQR: A Novel Enhanced Quantum Representation of Digital Images

> **Entry ID**: `zhang2015_neqr_edge`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Proposes NEQR (Novel Enhanced Quantum Representation), encoding pixel intensities as basis states (bitstrings) rather than rotation angles
- Enables deterministic pixel recovery upon measurement, unlike FRQI's probabilistic recovery
- Serves as the foundation for subsequent quantum edge detection algorithms using quantum comparators
- Requires more qubits (2n + q) than amplitude encoding (2k + 1) but offers exact pixel retrieval

---

## (B) Detailed Summary

### Problem Statement

The earlier FRQI (Flexible Representation of Quantum Images) encodes pixel intensity as a rotation angle on a single qubit, but measurement yields only probabilistic intensity recovery with low accuracy. Can we design a representation that allows exact pixel value retrieval?

### Core Idea

NEQR encodes each pixel's grayscale value (0–255) directly as an 8-qubit basis state. The position of each pixel is stored in 2n position qubits. This provides deterministic recovery of pixel values upon measurement, at the cost of additional qubits.

### Method

1. **NEQR encoding**: For a 2^n × 2^n image, use 2n position qubits + q intensity qubits (typically q=8 for 8-bit grayscale)
2. **Quantum comparator**: Compare adjacent pixel intensity registers using quantum comparison circuits
3. **Edge classification**: Mark positions where the intensity difference exceeds a threshold as edges
4. **Measurement and reconstruction**: Measure all qubits to reconstruct the edge map

### Results

- Deterministic pixel recovery (vs. FRQI's probabilistic recovery)
- Simulation shows edge maps comparable to classical methods
- Qubit overhead significantly higher than amplitude encoding approaches

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
|0⟩^{⊗(2n+q)} ─── [NEQR Encoding] ─── [Quantum Comparator] ─── [Measure]
                     ↓                        ↓
               Position(2n) + Intensity(q)  Adjacent pixel diff > threshold?
```

### Key Equations

**NEQR representation**:

$$|I\rangle_{NEQR} = \frac{1}{2^n} \sum_{y=0}^{2^n-1} \sum_{x=0}^{2^n-1} |f(y,x)\rangle |y\rangle |x\rangle$$

where $|f(y,x)\rangle = |c_{q-1} c_{q-2} \ldots c_0\rangle$ is the binary encoding of pixel (y, x)'s grayscale value.

---

## (D) Strengths / Contributions

- Deterministic pixel recovery upon measurement (solves FRQI's probabilistic recovery problem)
- Intuitive edge detection via quantum comparison circuits
- Systematic analysis of basis encoding trade-offs
- Foundation for many subsequent NEQR-based QED algorithms

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | Qubit count 2n+q is much larger than amplitude encoding's 2k+1 |
| Noise sensitivity | Many qubits make execution on NISQ devices impractical |
| Scalability | 256×256 image needs 16+8=24 qubits (near current hardware limits) |
| Reproducibility | Simulation only; no hardware experiments provided |

---

## (F) Comparison / Baselines

| Method | Qubit Count | Encoding Accuracy | Edge Detection | Practicality |
|--------|-------------|-------------------|----------------|-------------|
| NEQR (this paper) | 2n + q | Deterministic | Quantum comparator | Limited by qubit count |
| FRQI | 2n + 1 | Probabilistic | Limited | Fewer qubits |
| QHED (Yao 2017) | 2k + 1 | Probabilistic | Hadamard-based | Fewer qubits |
| Classical Sobel | N/A | Exact | Convolution | Mature technology |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, NumPy |
| Dataset | Small-scale grayscale images |
| Qubit count | 2n + q (4×4 image: 4+8=12 qubits) |
| Circuit depth | O(2^{2n} × q) |
| Execution environment | Simulator only |
| Runtime / cost | Simulation: grows exponentially with qubit count |
| Code availability | Not publicly available |

---

## (H) Keywords / Tags

- **Data encoding**: basis
- **Edge definition**: gradient
- **Circuit type**: comparator
- **Noise-aware**: no
- **Evaluation**: visual, complexity

---

## (I) Citation

```bibtex
@article{zhang2013neqr,
  title   = {NEQR: a novel enhanced quantum representation of digital images},
  author  = {Zhang, Yi and Lu, Kai and Gao, Yinghui and Wang, Mo},
  journal = {Quantum Information Processing},
  volume  = {12},
  number  = {8},
  pages   = {2833--2860},
  year    = {2013},
  doi     = {10.1007/s11128-013-0567-z},
}
```

**Link**: [https://doi.org/10.1007/s11128-013-0567-z](https://doi.org/10.1007/s11128-013-0567-z)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

---

## (K) Open Questions / Future Research Ideas

- Can a hybrid approach combining NEQR and amplitude encoding balance qubit count and accuracy?
- How can quantum comparator circuit depth be optimized?
- Would QRAM (if realized) eliminate NEQR's encoding bottleneck?
