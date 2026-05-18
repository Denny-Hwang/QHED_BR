"""Page 1 — Research Overview."""

import streamlit as st


def render() -> None:
    st.title("Quantum Hadamard Edge Detection with Boundary Restoration")
    st.markdown("**Sungjoo Hwang** | NISQ-Era Quantum Image Processing")

    st.markdown("---")

    st.header("Introduction")
    st.markdown("""
Edge detection is a fundamental operation in computer vision and image processing.
It identifies boundaries within images where pixel intensity changes sharply.
Classical algorithms (Sobel, Canny, etc.) work well but have computational complexity
that grows with image size -- typically **O(n^2)** for an image with *n* pixels.

**Quantum computing** offers a potentially faster alternative.
The **Quantum Hadamard Edge Detection (QHED)** algorithm encodes an image into
a quantum state and uses Hadamard gates to extract edge information in **O(1)** quantum operations
(after the encoding step).
""")

    st.header("How Quantum Image Processing Works")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("#### Digital Image")
        st.info("Classical pixel data")
    with col2:
        st.markdown("#### Encoding (C -> Q)")
        st.info("Amplitude encoding into quantum state")
    with col3:
        st.markdown("#### Quantum Circuit")
        st.info("Hadamard + Permutation gates")
    with col4:
        st.markdown("#### Measurement")
        st.info("Extract quantum state")
    with col5:
        st.markdown("#### Decoding (Q -> C)")
        st.info("Classical post-processing")

    st.markdown("""
The procedure of quantum image processing:

1. **Encoding (Classical -> Quantum):** The pixel values of the image are normalized
   and encoded as amplitudes of a quantum state vector. For a `2^k x 2^k` image,
   this requires `2k` data qubits plus 1 ancilla qubit.

2. **Quantum Computation:** The QHED circuit applies:
   - A Hadamard gate on the ancilla qubit
   - An amplitude permutation unitary `D_{2n-1}` (cyclic shift) across all qubits
   - Another Hadamard gate on the ancilla qubit

3. **Measurement & Decoding:** The statevector is measured. Odd-indexed amplitudes
   encode the *difference* between adjacent pixels -- i.e., the edges.
""")

    st.header("QHED Algorithm Details")

    st.markdown("""
The core idea: given pixel amplitudes encoded in the quantum state, the Hadamard-based
circuit computes the *difference* between adjacent pixel pairs. Positions where this
difference is large correspond to edges.

**Quantum Circuit Structure:**

| Component | Description |
|-----------|-------------|
| `ancilla` qubit | Initialized to \\|0>, Hadamard applied before and after permutation |
| `pixel` qubits | Encode the image amplitude via `initialize` gate |
| `D_{2n-1}` unitary | Cyclic right-shift of identity matrix -- permutes amplitudes |
| Measurement | Extract odd-indexed amplitudes = edge information |

**Key advantage:** The edge detection operation itself is **O(1)** in terms of quantum gate depth
(constant number of operations regardless of image size). The bottleneck is the encoding step at **O(n^2)**.
""")

    st.header("Boundary Restoration Method")
    st.markdown("""
### The Problem
In the NISQ era, qubits are limited. To process a large image (e.g., 256x256)
with only a few qubits, we must divide the image into small patches
(e.g., 4x4 with 2 pixel qubits). Each patch is processed independently.

**However**, this creates information loss at patch boundaries, because edge
information between adjacent patches is never computed.

### The Solution: Overlapping Patches with Majority Voting

1. Process the image with overlapping patches (stride < patch size)
2. Each pixel may be covered by multiple patches
3. For each pixel, perform **majority voting** across all patches that cover it
4. If more than half the patches detect an edge at that pixel, mark it as an edge

This restores the lost boundary information with only a **polynomial increase** in computation:
""")

    st.latex(r"""
\text{Without BR: stride} = p, \quad Q = \left\lceil\frac{N}{p}\right\rceil^2 \text{ patches}
""")
    st.latex(r"""
\text{With BR: stride} = p - 2, \quad Q = \left\lceil\frac{N - 2}{p - 2}\right\rceil^2 \text{ patches (2-pixel overlap)}
""")
    st.latex(r"""
\text{Total Time Complexity: } Q \cdot O(1) \text{ where } Q = \text{number of patches}
""")

    st.markdown("""
**Result:** Large-sized image boundaries can be effectively detected even with a limited-qubit
quantum processor, only by increasing the amount of computation in polynomial time.
""")

    st.header("Method Summary")
    st.markdown("""
| Property | Value |
|----------|-------|
| **Method** | BR_QHED (Boundary Restoration QHED) |
| **Qubits Required** | ceil(log2(N)) data + 1 ancilla |
| **Encoding Complexity** | O(n^2) |
| **Edge Detection Complexity** | Q * O(1), Q = number of patches |
| **Boundary Restoration** | Majority voting on overlapping patches |
""")
