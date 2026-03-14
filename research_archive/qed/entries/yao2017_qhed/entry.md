# Quantum Image Processing and Its Application to Edge Detection: Theory and Experiment

> **Entry ID**: `yao2017_qhed`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Proposes the QHED algorithm using a Hadamard gate and cyclic permutation unitary (D_{2n-1}) for quantum image edge detection
- Achieves O(n) detection complexity by computing adjacent pixel differences via quantum parallelism (vs. classical O(n²))
- First experimental demonstration on an IBM 4-qubit quantum processor with a 2×2 image
- Establishes the foundational theoretical framework for amplitude-encoded quantum edge detection

---

## (B) Detailed Summary

### Problem Statement

Classical edge detection algorithms (Sobel, Canny, etc.) require O(n²) operations for an image with n pixels. Can quantum parallelism offer a meaningful speedup?

### Core Idea

Encode image pixel intensities as amplitudes of a quantum state, then apply a Hadamard gate on an ancilla qubit combined with a cyclic permutation unitary on the data qubits. Post-selecting on the ancilla being |1⟩ yields a probability distribution proportional to adjacent pixel differences — i.e., edge information.

### Method

1. **Amplitude encoding**: Normalize the pixel values of a 2^k × 2^k image and encode them as amplitudes of a (2k+1)-qubit state
2. **Quantum operation**: Apply Hadamard to the first (ancilla) qubit and D_{2n-1} cyclic permutation to the remaining data qubits
3. **Measurement**: Post-select on the ancilla qubit being |1⟩; the resulting probability distribution encodes adjacent pixel differences
4. **Edge map reconstruction**: Extract edge intensities from the measurement probabilities

### Results

- Theoretical O(n) complexity for the detection stage (excluding encoding)
- Experimental verification on IBM ibmqx2 (5-qubit) processor for 2×2 images
- Qualitative agreement between simulation and hardware results

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
|0⟩ ─── [Amplitude Encoding] ─── H ─────── [Measure] ─── Post-select |1⟩
|0⟩ ─── [Amplitude Encoding] ─── D_{2n-1} ─ [Measure]
 ...           ...                    ...         ...
|0⟩ ─── [Amplitude Encoding] ─── D_{2n-1} ─ [Measure]
```

### Key Equations

**Amplitude encoding**:

$$|I\rangle = \frac{1}{\sqrt{\sum_j c_j^2}} \sum_{j=0}^{2^{2k}-1} c_j |0\rangle|j\rangle$$

where $c_j$ is the normalized intensity of pixel $j$.

**After Hadamard + D_{2n-1}**:

$$|\psi\rangle = \frac{1}{2}\sum_j (c_j + c_{j \oplus (2^{2k}-1)})|0\rangle|j\rangle + \frac{1}{2}\sum_j (c_j - c_{j \oplus (2^{2k}-1)})|1\rangle|j\rangle$$

Post-selecting on ancilla = |1⟩ yields probabilities proportional to $|c_j - c_{j'}|^2$.

---

## (D) Strengths / Contributions

- First systematic theoretical framework for quantum edge detection with experimental validation
- Detection stage achieves O(n) complexity (exponential speedup over classical O(n²))
- Amplitude encoding enables exponential compression (2^k × 2^k image in 2k+1 qubits)
- Hardware experiment on IBM quantum processor demonstrates practical feasibility

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | Amplitude encoding requires O(n²) gates, potentially negating quantum advantage end-to-end |
| Noise sensitivity | Gate errors and decoherence on real hardware degrade result quality |
| Scalability | Only 2×2 images tested on hardware; larger images remain untested experimentally |
| Boundary artifacts | Patch-based processing loses edge info at patch boundaries (no boundary restoration) |
| Reproducibility | Requires IBM quantum hardware access; qubit limits prevent practical-scale images |

---

## (F) Comparison / Baselines

| Method | Detection Complexity | Encoding Complexity | Pros | Cons |
|--------|---------------------|---------------------|------|------|
| QHED (this paper) | O(n) | O(n²) | Exponential speedup in detection | Encoding bottleneck, small-scale experiments |
| Classical Sobel | O(n²) | N/A | Mature technology, noise-robust | Slow for very large images |
| Classical Canny | O(n²) | N/A | High-quality edge detection | Requires parameter tuning |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit (>=1.0), NumPy, Matplotlib |
| Dataset | Arbitrary 2×2, 4×4 grayscale images |
| Qubit count | 2k+1 (2×2 image: 5 qubits, 4×4 image: 9 qubits) |
| Circuit depth | O(n²) (dominated by amplitude encoding) |
| Execution environment | IBM ibmqx2 (5-qubit), Qiskit Aer simulator |
| Runtime / cost | Simulation: seconds / Hardware: minutes including queue |
| Code availability | Circuit description in paper; no public repository |

---

## (H) Keywords / Tags

- **Data encoding**: amplitude
- **Edge definition**: gradient
- **Circuit type**: hadamard
- **Noise-aware**: partial
- **Evaluation**: visual, complexity

---

## (I) Citation

```bibtex
@article{yao2017quantum,
  title   = {Quantum Image Processing and Its Application to Edge Detection: Theory and Experiment},
  author  = {Yao, Xi-Wei and Wang, Hengyan and Liao, Zeyang and Chen, Ming-Cheng and Pan, Jian and Li, Jun and Zhang, Kechao and Lin, Xingcheng and Wang, Zhehui and Luo, Zhihuang and others},
  journal = {Physical Review X},
  volume  = {7},
  number  = {3},
  pages   = {031041},
  year    = {2017},
  doi     = {10.1103/PhysRevX.7.031041},
}
```

**Link**: [https://doi.org/10.1103/PhysRevX.7.031041](https://doi.org/10.1103/PhysRevX.7.031041)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

![Comparison Table](../../figures/qed_comparison_table.svg)

---

## (K) Open Questions / Future Research Ideas

- How does approximate amplitude encoding affect edge detection quality?
- Can boundary restoration (overlapping patches) significantly improve full-image edge maps?
- What is the effect of error mitigation techniques on NISQ device results?
- Can the approach be extended to multi-channel (color) images?
