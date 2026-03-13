# Quantum Image Edge Detection Based on Laplacian Operator and Zero-Cross Method

> **Entry ID**: `fan2019_quantum_laplacian`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Implements the Laplacian operator as a quantum circuit for isotropic image edge detection
- Uses second-order derivatives instead of first-order (gradient), eliminating directional bias
- Combines FRQI/NEQR encoding with quantum shift operators to access 4-neighbor pixels
- Simulation results match classical Laplacian filtering, but circuit complexity is higher than gradient-based methods

---

## (B) Detailed Summary

### Problem Statement

First-order derivative (gradient) based quantum edge detection is biased toward certain directions. Can a second-order derivative (Laplacian) quantum circuit achieve isotropic (direction-independent) edge detection?

### Core Idea

Design quantum operations corresponding to the classical Laplacian kernel $\begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$. By applying cyclic shift operations on position qubits, the algorithm accesses the four neighboring pixels and computes their weighted difference with the center pixel.

### Method

1. **Quantum image encoding**: Encode the image using FRQI or NEQR representation
2. **Quantum Laplacian operation**: Apply shift unitaries on position registers to access 4-directional neighbors, then compute the weighted sum/difference
3. **Ancilla storage**: Store the Laplacian result in ancilla qubits
4. **Measurement and thresholding**: Measure ancilla qubits to extract edge intensities

### Results

- Isotropic edge detection with no directional bias
- Simulation quality comparable to classical Laplacian
- Circuit complexity higher than gradient-based methods due to 4-directional shift operations

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
|Image⟩ ─── [Shift UP] ──┐
|Image⟩ ─── [Shift DOWN] ─┤─── [Sum & Weight] ─── [Compare with center×4] ─── |Edge⟩
|Image⟩ ─── [Shift LEFT] ─┤
|Image⟩ ─── [Shift RIGHT]─┘
```

### Key Equations

**Discrete Laplacian**:

$$\nabla^2 f(x,y) = f(x+1,y) + f(x-1,y) + f(x,y+1) + f(x,y-1) - 4f(x,y)$$

**Quantum implementation via cyclic shift**:

$$U_{shift} |y,x\rangle = |y, x \oplus 1\rangle$$

---

## (D) Strengths / Contributions

- Isotropic edge detection: uniform edge sensitivity regardless of direction
- Systematic framework for implementing Laplacian in quantum circuits
- Demonstrates the feasibility of higher-order derivative quantum image processing

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | FRQI/NEQR encoding cost remains the dominant bottleneck |
| Noise sensitivity | Laplacian is inherently noise-sensitive (2nd derivative); quantum noise exacerbates this |
| Scalability | 4-directional shift operations increase circuit depth vs. gradient methods |
| Reproducibility | Simulation only; no hardware experiments |

---

## (F) Comparison / Baselines

| Method | Edge Definition | Isotropic | Noise Robustness | Circuit Complexity |
|--------|----------------|-----------|-------------------|-------------------|
| This paper (Q-Laplacian) | 2nd derivative | Yes | Low | High |
| QHED (gradient) | 1st derivative | No | Medium | Low |
| Classical Laplacian | 2nd derivative | Yes | Low | O(n²) |
| Classical Canny | 1st derivative + NMS | Yes | High | O(n²) |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, NumPy |
| Dataset | Small-scale grayscale test images |
| Qubit count | 2n + q + ancilla (more than gradient methods) |
| Circuit depth | O(n²)+ (4-directional shift + comparison) |
| Execution environment | Simulator only |
| Runtime / cost | Simulation: 2-4× slower than gradient methods |
| Code availability | Not publicly available |

---

## (H) Keywords / Tags

- **Data encoding**: amplitude
- **Edge definition**: laplacian
- **Circuit type**: shift_operator
- **Noise-aware**: no
- **Evaluation**: visual, complexity

---

## (I) Citation

```bibtex
@article{fan2019quantum,
  title   = {Quantum image edge detection based on Laplacian operator and zero-cross method},
  author  = {Fan, Ping and Zhou, Ri-Gui and Hu, WenWen and Jing, Naihuan},
  journal = {Quantum Information Processing},
  volume  = {18},
  pages   = {1--23},
  year    = {2019},
  doi     = {10.1007/s11128-019-2270-x},
}
```

**Link**: [https://doi.org/10.1007/s11128-019-2270-x](https://doi.org/10.1007/s11128-019-2270-x)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

---

## (K) Open Questions / Future Research Ideas

- Can combining quantum Laplacian with smoothing pre-processing reduce noise sensitivity?
- Is a quantum Laplacian of Gaussian (LoG) implementation feasible?
- Could a hybrid gradient + Laplacian quantum edge detector capture the best of both approaches?
