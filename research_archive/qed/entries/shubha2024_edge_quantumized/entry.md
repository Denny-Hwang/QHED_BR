# Edge Detection Quantumized: A Novel Quantum Algorithm for Image Processing

> **Entry ID**: `shubha2024_edge_quantumized`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR

- Modifies the original QHED algorithm to handle complex (non-binary) images via dynamic threshold adjustment
- Introduces FRQI-based encoding as an alternative to amplitude encoding for more flexible circuit design
- Proposes a noise filtering mechanism using classical-quantum hybrid post-processing
- Extends QHED applicability from simple binary images to real-world grayscale/color images

---

## (B) Detailed Summary

### Problem Statement

The original QHED algorithm (Yao 2017) works primarily on binary or near-binary images using QPIE (Quantum Probability Image Encoding). Real-world images with complex intensity distributions and noise produce poor edge maps. How can QHED be adapted for general-purpose images?

### Core Idea

Modify both the encoding and detection stages: (1) use FRQI encoding to handle wider intensity ranges, (2) add a dynamic threshold that adapts to image content, and (3) apply classical post-processing to filter noise from the quantum measurement output. This hybrid approach bridges the gap between idealized quantum edge detection and practical image processing.

### Method

1. **FRQI encoding**: Replace QPIE with FRQI for more flexible intensity representation, enabling partial measurement techniques
2. **Modified QHED circuit**: Adapt the Hadamard + permutation circuit with parametric adjustments for non-binary images
3. **Dynamic thresholding**: Analyze relative edge intensities and apply a hyperparameter-controlled threshold to suppress noise
4. **Classical-quantum hybrid**: Post-process quantum measurement results with classical filtering for cleaner edges

### Results

- Successfully detects edges in complex real-world images (not just binary)
- Improved edge outlines through modified edge detection ordering
- Noise filtering significantly improves result quality
- Maintains constant-time detection complexity O(1) independent of image size

---

## (C) Mechanism / Principles

### Quantum Circuit / Computation Flow

```
Classical Image ─── [FRQI Encoding] ─── [Modified QHED Circuit] ─── [Partial Measurement]
                                              ↓
                                    [Dynamic Thresholding]
                                              ↓
                                    [Classical Noise Filter] ─── Edge Map
```

### Key Equations

**FRQI encoding**:

$$|I\rangle = \frac{1}{2^n}\sum_{i=0}^{2^{2n}-1}(\cos\theta_i|0\rangle + \sin\theta_i|1\rangle) \otimes |i\rangle$$

**Dynamic threshold**: $T = \alpha \cdot \text{median}(\{p_j\})$ where $p_j$ are measured edge probabilities and $\alpha$ is a tunable hyperparameter.

---

## (D) Strengths / Contributions

- Makes QHED practical for real-world (non-binary) images
- Dynamic thresholding adapts to image content automatically
- Hybrid classical-quantum pipeline balances quantum speedup with classical robustness
- Maintains O(1) detection complexity (constant-time, image-size independent)

---

## (E) Limitations / Weaknesses

| Limitation | Description |
|------------|-------------|
| Encoding cost | FRQI encoding still requires O(2^{2n}) gates |
| Classical overhead | Post-processing adds classical computation; not purely quantum |
| Threshold sensitivity | Dynamic threshold depends on hyperparameter α tuning |
| Hardware validation | No real quantum hardware experiments reported |
| Reproducibility | arXiv preprint; no public code repository |

---

## (F) Comparison / Baselines

| Method | Image Types | Detection Complexity | Noise Handling | Hybrid |
|--------|-------------|---------------------|----------------|--------|
| This paper (modified QHED) | General grayscale/color | O(1) | Dynamic threshold + classical filter | Yes |
| Original QHED (Yao 2017) | Binary / near-binary | O(n) | None | No |
| QSobel (Yi 2015) | Grayscale (FRQI) | O(n²) | None | No |
| Classical Canny | General | O(n²) | Gaussian smoothing + NMS | No |

---

## (G) Reproduction / Implementation Notes

| Item | Details |
|------|---------|
| Libraries required | Qiskit, NumPy, OpenCV (post-processing) |
| Dataset | Various grayscale and color images |
| Qubit count | 2n + 1 (FRQI) |
| Circuit depth | O(2^{2n}) for encoding, O(1) for detection |
| Execution environment | Simulator (Qiskit Aer) |
| Runtime / cost | Simulation: seconds for small images |
| Code availability | Not publicly available (arXiv preprint) |

---

## (H) Keywords / Tags

- **Data encoding**: FRQI
- **Edge definition**: gradient
- **Circuit type**: hadamard
- **Noise-aware**: partial
- **Evaluation**: visual, complexity

---

## (I) Citation

```bibtex
@article{shubha2024edge,
  title   = {Edge Detection Quantumized: A Novel Quantum Algorithm for Image Processing},
  author  = {Shubha, Syed Emad Uddin and Islam, Mir Muzahedul and Sadi, Tanvir Ahahmed and Miraz, Md. Hasibul Hasan and Mahdy, M. R. C.},
  journal = {arXiv preprint arXiv:2404.06889},
  year    = {2024},
}
```

**Link**: [https://arxiv.org/abs/2404.06889](https://arxiv.org/abs/2404.06889)

---

## (J) Figures / Diagrams

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

---

## (K) Open Questions / Future Research Ideas

- How does the dynamic threshold compare to adaptive classical thresholding (e.g., Otsu's method)?
- Can the classical post-processing step be replaced by a quantum noise filter?
- What is the optimal α hyperparameter for different image categories?
- Is the O(1) detection claim robust when accounting for measurement shot noise?
