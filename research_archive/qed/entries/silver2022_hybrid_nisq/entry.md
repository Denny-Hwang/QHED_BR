# A Hybrid Quantum Image Edge Detector for the NISQ Era

> **Entry ID**: `silver2022_hybrid_nisq`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Proposes a hybrid classical-quantum edge detector specifically designed for NISQ (Noisy Intermediate-Scale Quantum) constraints
- Based on a quantum artificial neuron (QAN) model that requires very few gates per circuit
- Each circuit's error is independent of image size, making it robust to scaling
- Demonstrates practical NISQ-compatible quantum edge detection with noise resilience

---

## (B) Detailed Summary

### Problem Statement

Most quantum edge detection algorithms require deep circuits with many qubits, making them impractical on current NISQ hardware with high error rates. Can we design a quantum edge detector that works within NISQ constraints (few qubits, shallow circuits, high noise)?

### Core Idea

Use a quantum artificial neuron (QAN) — a parameterized quantum circuit acting as a nonlinear classifier — to determine whether a pixel is an edge pixel based on its local neighborhood. The QAN processes small patches of the image, with each circuit execution requiring only a few qubits and gates. Since the circuit size depends on the patch (not the image), the error per circuit is image-size independent.

### Method

1. **Patch extraction**: Classically extract small local patches around each pixel
2. **Quantum artificial neuron**: Encode the patch into a few-qubit circuit and apply parameterized gates trained to classify edge vs. non-edge
3. **Training**: Use classical optimization to train the QAN parameters on labeled edge/non-edge examples
4. **Inference**: Apply the trained QAN to all patches to produce the full edge map

### Results

- Successfully detects edges on real images using shallow quantum circuits
- Noise resilience: circuit error independent of image size
- Few-qubit circuits (typically 3-5 qubits) compatible with current NISQ processors
- Trained model generalizes across different image types
- Practical demonstration on quantum simulators with realistic noise models

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
Pixel Patch (3×3) ─── [Angle Encoding] ─── [Parameterized Layers (RY, CNOT)] ─── [Measure q0]
                                                                                       ↓
                                                                               Edge / Non-edge
```

### Key Equations

**QAN circuit**: A parameterized unitary $U(\theta)$ applied to an encoded input:

$$|\psi_{out}\rangle = U(\theta) \cdot U_{enc}(x) |0\rangle^{\otimes n}$$

**Classification**: $P(\text{edge}) = |\langle 1| \otimes I^{n-1} |\psi_{out}\rangle|^2$

**Training**: Minimize cross-entropy loss over labeled training set via classical optimizer.

---

## (D) Strengths / Contributions

- Explicitly designed for NISQ constraints: few qubits, shallow circuits
- Error per circuit is independent of image size (scalable in terms of noise)
- Trainable: adapts to different edge detection criteria via training data
- Hybrid approach leverages classical pre/post-processing efficiently
- Demonstrates practical quantum advantage pathway for image processing

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Training required | Needs labeled edge detection data for training, unlike direct algorithmic approaches |
| No quantum speedup | No theoretical speedup over classical methods; advantage is in noise resilience |
| Patch-based | Processes patches independently; may miss global context |
| Encoding cost | Angle encoding per patch is simple but must be repeated for each pixel |
| Scalability | One circuit per pixel means total runtime scales with image size |

---

## (F) Comparison / Baselines

| Method | NISQ Compatible | Qubits | Training | Speedup | Noise Robust |
|--------|----------------|--------|----------|---------|-------------|
| This paper (hybrid QAN) | Yes | 3-5 | Yes | No | Yes |
| QHED (Yao 2017) | Partially | 2k+1 | No | O(n) | No |
| QSobel variants | No | 2n+q | No | Varies | No |
| Classical CNN edge det. | N/A | N/A | Yes | N/A | N/A |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, PennyLane, or Cirq; NumPy, scikit-learn |
| Dataset | Edge detection datasets (e.g., BSDS500 patches) |
| Qubit count | 3-5 qubits per circuit |
| Circuit depth | Very shallow (2-4 layers) |
| Execution environment | NISQ hardware or noisy simulator |
| Runtime / cost | One circuit per pixel; parallelizable |
| Code availability | Not specified |

---

## (H) Keywords / Tags

- **Data encoding**: angle
- **Edge definition**: variational
- **Circuit type**: variational
- **Noise-aware**: yes
- **Evaluation**: quantitative, visual

---

## (I) Citation

```bibtex
@article{silver2022hybrid,
  title   = {A hybrid quantum image edge detector for the NISQ era},
  author  = {Silver-Thorn, Travis and others},
  journal = {Quantum Machine Intelligence},
  volume  = {4},
  pages   = {16},
  year    = {2022},
  doi     = {10.1007/s42484-022-00071-3},
}
```

**Link**: [https://doi.org/10.1007/s42484-022-00071-3](https://doi.org/10.1007/s42484-022-00071-3)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

---

## (K) Open Questions / Future Research Ideas

- Can the QAN approach be combined with quantum kernel methods for better feature extraction?
- What happens when training on one image domain and testing on another (transfer learning)?
- Can the per-pixel circuit be batched or parallelized on multi-QPU systems?
- How does the QAN compare to classical tiny neural networks with the same parameter count?
