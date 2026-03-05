# QHED-BR: Quantum Hadamard Edge Detection with Boundary Restoration

A quantum image processing application that demonstrates edge detection using the **Quantum Hadamard Edge Detection (QHED)** algorithm with a **Boundary Restoration** method for processing large images with limited qubits in the NISQ era.

## Overview

Classical edge detection algorithms (Sobel, Canny, etc.) have **O(n^2)** time complexity for an image with n pixels. QHED encodes the image into a quantum state using amplitude encoding, then detects edges in **O(1)** quantum operations by leveraging Hadamard gates and an amplitude permutation unitary.

**The problem:** In the NISQ era, qubits are scarce. A 256x256 image requires 17 qubits for direct encoding. With only a few qubits available, the image must be split into patches, causing information loss at patch boundaries.

**Our solution:** Overlapping patches with majority voting restores the lost boundary information, requiring only polynomial additional computation.

### Key Properties

| Property | Value |
|----------|-------|
| Method | BR_QHED (Boundary Restoration QHED) |
| Qubits Required | ceil(log2(N)) data + 1 ancilla |
| Encoding Complexity | O(n^2) |
| Edge Detection | Q * O(1), where Q = number of patches |
| Boundary Restoration | Majority voting on overlapping patches |

## Project Structure

```
QHED_BR/
├── app.py                  # Streamlit web application
├── qhed.py                 # Core QHED algorithm (statevector & QASM)
├── basicFunctions.py       # Image loading, encoding utilities
├── classical_ed_methods.py # Sobel, Prewitt, Laplacian, Canny
├── requirements.txt        # Python dependencies
├── images/                 # Sample test images
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Denny-Hwang/QHED_BR.git
cd QHED_BR

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Streamlit Web App

```bash
streamlit run app.py
```

The app provides four pages:

1. **Research Overview** - Explanation of QHED, boundary restoration method, and the algorithm's advantages
2. **QHED Circuit Explained** - Interactive circuit generation and step-by-step visualization
3. **Interactive Edge Detection** - Upload your own image or use samples to:
   - Run QHED with adjustable qubits and threshold
   - Compare with/without boundary restoration
   - Run classical edge detection (Sobel, Canny, Prewitt, Laplacian)
   - Side-by-side quantum vs classical comparison
   - Download result images
4. **Complexity Comparison** - Charts and tables comparing quantum vs classical complexity

### Python API

```python
from basicFunctions import load_image
from qhed import QHED, edge_detection_stride

# Load and preprocess image
image = load_image('images/22.png', resize=(64, 64))

# Small image: direct QHED
edges = QHED(image, thr_ratio=0.7)

# Large image: patch-based with boundary restoration
edges_br, n_patches = edge_detection_stride(
    image,
    width_qb=2,            # 4x4 patches (2^2)
    thr_ratio=0.5,
    stride_mode='with_restoration',  # overlapping patches
)
```

## Algorithm Details

### QHED Circuit

```
|0> ──── H ──── D_{2n-1} ──── H ──── Measure   (ancilla)
|p> ──── Init ─────────────────────── Measure   (pixel qubits)
```

1. Pixel values are amplitude-encoded into data qubits
2. Hadamard gate puts the ancilla into superposition
3. The cyclic permutation unitary `D_{2n-1}` shifts basis states
4. Second Hadamard on ancilla creates interference
5. Odd-indexed amplitudes in the output encode pixel differences (edges)

### Boundary Restoration

When processing large images with limited qubits:
- **Without BR:** Image is split into non-overlapping patches. Boundary pixels between patches lose edge information.
- **With BR:** Patches overlap by 1 pixel. Each pixel is covered by multiple patches. Majority voting across patches restores boundary edges.

## Dependencies

- **Qiskit 2.x** + **qiskit-aer** - Quantum circuit simulation
- **NumPy** - Numerical computation
- **OpenCV** - Classical image processing
- **Matplotlib** - Visualization
- **Streamlit** - Web application framework
- **Pillow** - Image I/O

## References

- Yao, Xi-Wei, et al. "Quantum image processing and its application to edge detection: theory and experiment." Physical Review X 7.3 (2017): 031041.
- [Qiskit](https://qiskit.org/) - Open-source quantum computing SDK
- [IBM Quantum](https://quantum-computing.ibm.com/)
- Hwang, S. "Boundary Restoration Method of Quantum Edge Detection in Restricted Qubits in NISQ Era"

## License

This project is for research and educational purposes.
