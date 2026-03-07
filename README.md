# QHED-BR: Quantum Hadamard Edge Detection with Boundary Restoration

A quantum image processing application that demonstrates edge detection using the **Quantum Hadamard Edge Detection (QHED)** algorithm with a **Boundary Restoration (BR)** method for processing large images with limited qubits in the NISQ era.

## Overview

Classical edge detection algorithms (Sobel, Canny, etc.) have **O(n²)** time complexity for an image with n pixels. QHED encodes the image into a quantum state using amplitude encoding, then detects edges in **O(1)** quantum operations by leveraging Hadamard gates and an amplitude permutation unitary.

**The problem:** In the NISQ era, qubits are scarce. A 256×256 image requires 17 qubits for direct encoding. With only a few qubits available, the image must be split into patches, causing information loss at patch boundaries.

**Our solution:** Overlapping patches (stride = p − 2) with majority voting restores the lost boundary information, requiring only polynomial additional computation. The 2-pixel overlap ensures that boundary-zeroed pixels in one patch are interior (and thus computed) in an adjacent patch.

### Key Properties

| Property | Value |
|----------|-------|
| Method | BR_QHED (Boundary Restoration QHED) |
| Qubits Required | 2k data + 1 ancilla (for 2^k × 2^k patches) |
| Encoding Complexity | O(p²) quantum gates per patch |
| Edge Detection | O(k) quantum gates per patch (exponential speedup) |
| Boundary Restoration | stride = p − 2, interior-mask counting, majority voting |
| Space Advantage | Exponential: 2^(2k) classical → (2k+1) qubits |

## Project Structure

```
QHED_BR/
├── app.py                  # Streamlit web application (5 pages)
├── qhed.py                 # Core QHED algorithm (statevector & QASM)
├── basicFunctions.py       # Image loading, encoding utilities
├── classical_ed_methods.py # Sobel, Prewitt, Laplacian, Canny
├── docs.py                 # Documentation utilities
├── requirements.txt        # Python dependencies
├── images/                 # Sample test images
│   ├── samples/            # General sample images
│   ├── license_plates/     # License plate test images
│   └── others/             # Additional test images
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Denny-Hwang/QHED_BR.git
cd QHED_BR

# Install dependencies
pip install -r requirements.txt

# Optional: for IBM Quantum hardware execution
pip install qiskit-ibm-runtime
```

## Usage

### Streamlit Web App

```bash
streamlit run app.py
```

The app provides five pages:

1. **Research Overview** — Explanation of QHED, boundary restoration method (stride = p − 2, interior-mask counting), and the algorithm's advantages
2. **QHED Circuit Explained** — Interactive circuit generation and step-by-step visualization of Hadamard gates, D_{2n-1} permutation unitary, and amplitude encoding
3. **Interactive Edge Detection** — Upload your own image or use samples to:
   - Run QHED with adjustable qubits (k ≥ 3, i.e., 8×8 patches minimum) and threshold
   - Compare with/without boundary restoration
   - Run classical edge detection (Sobel, Canny, Prewitt, Laplacian)
   - Side-by-side quantum vs classical comparison
   - Download result images
4. **Complexity Comparison** — Rigorous theoretical analysis with:
   - Case 1: Detection-only comparison (excluding encoding/decoding)
   - Case 2: End-to-end comparison (including encoding & readout)
   - Hardware speed ratio α for fair quantum vs classical comparison
   - Crossover threshold tables and visualization graphs
   - Space complexity: exponential memory advantage
   - BR overhead analysis
5. **IBM Quantum Hardware** — Run QHED on real IBM quantum processors:
   - Dual-channel authentication (IBM Cloud + IBM Quantum Platform)
   - Preferred Heron r2 backend selection (ibm_marrakesh, ibm_fez, ibm_torino)
   - Real hardware execution with SamplerV2
   - Progress tracking with ETA
   - Comparison with simulation results

### Python API

```python
from basicFunctions import load_image
from qhed import QHED, edge_detection_stride

# Load and preprocess image
image = load_image('images/samples/example.png', resize=(64, 64))

# Small image: direct QHED
edges = QHED(image, thr_ratio=0.7)

# Large image: patch-based with boundary restoration
edges_br, n_patches = edge_detection_stride(
    image,
    width_qb=3,                        # 8x8 patches (2^3), minimum supported
    thr_ratio=0.5,
    stride_mode='with_restoration',    # overlapping patches (stride = p-2)
    patch_boundary_zero=True,          # zero boundary pixels
)
```

## Algorithm Details

### QHED Circuit

```
|0⟩ ──── H ──── D_{2n-1} ──── H ──── Measure   (ancilla)
|ψ⟩ ──── Init ─────────────────────── Measure   (pixel qubits)
```

1. Pixel values are amplitude-encoded into 2k data qubits
2. Hadamard gate puts the ancilla into superposition
3. The cyclic permutation unitary `D_{2n-1}` (quantum increment circuit, O(k) Toffoli gates) shifts basis states
4. Second Hadamard on ancilla creates interference
5. Odd-indexed amplitudes in the output encode pixel differences (edges)

### Boundary Restoration

When processing large images with limited qubits:
- **Without BR:** Image is split into non-overlapping patches (stride = p). Boundary pixels between patches lose edge information.
- **With BR:** Patches overlap by 2 pixels (stride = p − 2). Combined with boundary zeroing, each pixel is interior in exactly one patch. The interior-mask ensures correct counting — only pixels that are truly computed (not boundary-zeroed) contribute to the majority vote.

### Complexity Summary

| Dimension | Classical | QHED-BR | Advantage |
|-----------|----------|---------|-----------|
| **Detection (per patch)** | O(p²) | O(k) gates | Exponential: p²/k speedup |
| **Encoding (per patch)** | — | O(p²) gates | Bottleneck for end-to-end |
| **Space (per patch)** | O(p²) memory | O(k) qubits | Exponential compression |
| **BR overhead** | — | (p/(p−2))² → 1 | Polynomial, vanishes |

## Dependencies

- **Qiskit 2.x** + **qiskit-aer** — Quantum circuit simulation
- **qiskit-ibm-runtime** — (Optional) IBM Quantum hardware execution
- **NumPy** — Numerical computation
- **OpenCV** — Classical image processing
- **Matplotlib** — Visualization
- **Streamlit** — Web application framework
- **Pillow** — Image I/O

## References

- Yao, Xi-Wei, et al. "Quantum image processing and its application to edge detection: theory and experiment." Physical Review X 7.3 (2017): 031041.
- Shende, Bullock & Markov, "Synthesis of quantum logic circuits," IEEE Trans. CAD, 2006
- Takahashi & Kunihiro, "A linear-size quantum circuit for addition with no ancillary qubits," Quantum Inf. Comput. 5(6), 2005
- [Qiskit](https://qiskit.org/) — Open-source quantum computing SDK
- [IBM Quantum](https://quantum-computing.ibm.com/)
- Hwang, S. "Boundary Restoration Method of Quantum Edge Detection in Restricted Qubits in NISQ Era"

## License

This project is for research and educational purposes.
