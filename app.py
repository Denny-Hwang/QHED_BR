"""
QHED-BR: Quantum Hadamard Edge Detection with Boundary Restoration
Interactive Streamlit Application
"""

import io
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import streamlit as st
from PIL import Image

from basicFunctions import load_image, load_image_from_array, amplitude_encode
from qhed import QHED, build_qhed_circuit, edge_detection_stride
from classical_ed_methods import (
    sobel_edge_detection,
    prewitt_edge_detection,
    laplacian_edge_detection,
    canny_edge_detection,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="QHED-BR: Quantum Edge Detection",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Helper: convert matplotlib figure to bytes for download
# ---------------------------------------------------------------------------
def fig_to_bytes(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()


def img_to_bytes(img_array, cmap='gray'):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img_array, cmap=cmap)
    ax.axis('off')
    data = fig_to_bytes(fig)
    plt.close(fig)
    return data


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "1. Research Overview",
        "2. QHED Circuit Explained",
        "3. Interactive Edge Detection",
        "4. Complexity Comparison",
    ],
)

# ===================================================================
# PAGE 1: Research Overview
# ===================================================================
if page == "1. Research Overview":
    st.title("Quantum Hadamard Edge Detection with Boundary Restoration")
    st.markdown("**Sungjoo Hwang** | NISQ-Era Quantum Image Processing")

    st.markdown("---")

    # --- Introduction ---
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

    # --- How Quantum Image Processing Works ---
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

    # --- QHED Algorithm ---
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

    # --- Boundary Restoration ---
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
\text{Without Restoration: } \left(\frac{N}{2^k}\right)^2 \text{ patches}
""")
    st.latex(r"""
\text{With Restoration: } \left(\frac{N}{2^k - 1}\right)^2 \text{ patches (overlap by 1)}
""")
    st.latex(r"""
\text{Total Time Complexity: } Q \cdot O(1) \text{ where } Q = \text{number of patches}
""")

    st.markdown("""
**Result:** Large-sized image boundaries can be effectively detected even with a limited-qubit
quantum processor, only by increasing the amount of computation in polynomial time.
""")

    # --- Summary Table ---
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


# ===================================================================
# PAGE 2: QHED Circuit Explained
# ===================================================================
elif page == "2. QHED Circuit Explained":
    st.title("QHED Quantum Circuit - Step by Step")

    st.markdown("""
    This page shows how the QHED quantum circuit is constructed and operates.
    You can generate a circuit for different image sizes and inspect it visually.
    """)

    st.header("1. Generate a QHED Circuit")

    col1, col2 = st.columns(2)
    with col1:
        patch_size_exp = st.selectbox(
            "Patch size (2^n x 2^n pixels)",
            [1, 2, 3],
            index=0,
            format_func=lambda x: f"{2**x}x{2**x} = {4**x} pixels ({2*x} data qubits + 1 ancilla)"
        )
    with col2:
        scan_dir = st.selectbox("Scan direction", ["horizontal", "vertical"])

    patch_size = 2 ** patch_size_exp
    st.info(f"Circuit uses **{2 * patch_size_exp + 1} qubits** total "
            f"({2 * patch_size_exp} data + 1 ancilla) for a {patch_size}x{patch_size} patch.")

    # Create a sample gradient image for demo
    sample = np.zeros((patch_size, patch_size))
    for i in range(patch_size):
        for j in range(patch_size):
            sample[i, j] = (i + j) / (2 * patch_size - 2) if patch_size > 1 else 0.5

    qc = build_qhed_circuit(sample, scan=scan_dir)
    if qc is not None:
        fig = qc.draw('mpl', fold=-1)
        st.pyplot(fig)
        plt.close()

        st.download_button(
            "Download circuit diagram",
            fig_to_bytes(fig),
            file_name="qhed_circuit.png",
            mime="image/png"
        )
    else:
        st.warning("Could not build circuit (uniform image).")

    # --- Step-by-step explanation ---
    st.header("2. Circuit Operation Step by Step")

    st.markdown(f"""
    **For a {patch_size}x{patch_size} image ({patch_size*patch_size} pixels):**

    | Step | Operation | Description |
    |------|-----------|-------------|
    | 1 | `Initialize` | Encode {patch_size*patch_size} pixel amplitudes into {2*patch_size_exp} data qubits |
    | 2 | `H(ancilla)` | Put ancilla qubit into superposition |
    | 3 | `D_{{2n-1}}` | Apply cyclic permutation unitary across all {2*patch_size_exp+1} qubits |
    | 4 | `H(ancilla)` | Second Hadamard on ancilla |
    | 5 | `Measure` | Read out all qubits |

    **After measurement**, the odd-indexed components of the statevector encode the
    *differences* between adjacent pixels. Large differences = edges.
    """)

    # --- Encoding visualization ---
    st.header("3. Amplitude Encoding Visualization")

    st.markdown("""
    The image pixel values are normalized so that the sum of squares equals 1,
    then used as amplitudes of a quantum state:
    """)
    st.latex(r"|image\rangle = \sum_{i=0}^{N-1} p_i |i\rangle, \quad \sum_i |p_i|^2 = 1")

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.imshow(sample, cmap='gray')
    ax1.set_title(f'Sample {patch_size}x{patch_size} Image')
    ax1.axis('off')

    encoded = amplitude_encode(sample)
    if encoded is not None:
        ax2.bar(range(len(encoded)), encoded, color='steelblue')
        ax2.set_title('Amplitude-Encoded State Vector')
        ax2.set_xlabel('Basis State Index')
        ax2.set_ylabel('Amplitude')
    st.pyplot(fig2)
    plt.close(fig2)

    # --- Permutation Matrix ---
    st.header("4. Permutation Unitary D_{2n-1}")
    st.markdown("""
    The permutation unitary is a cyclic right-shift of the identity matrix.
    It shifts each basis state |i> to |i+1 mod 2^n>.
    This operation, combined with the Hadamard gates on the ancilla,
    effectively computes the difference between adjacent pixel pairs.
    """)

    total_qb = 2 * patch_size_exp + 1
    D = np.roll(np.identity(2 ** total_qb), 1, axis=1)
    fig3, ax3 = plt.subplots(figsize=(5, 5))
    ax3.imshow(D[:16, :16] if D.shape[0] > 16 else D, cmap='Blues')
    ax3.set_title(f'D_{{2n-1}} (showing top-left 16x16)')
    ax3.set_xlabel('Column')
    ax3.set_ylabel('Row')
    st.pyplot(fig3)
    plt.close(fig3)


# ===================================================================
# PAGE 3: Interactive Edge Detection
# ===================================================================
elif page == "3. Interactive Edge Detection":
    st.title("Interactive Edge Detection")
    st.markdown("Upload your own image or use a sample image to compare quantum and classical edge detection.")

    # --- Image Source ---
    st.header("1. Select Image")

    image_source = st.radio("Image source", ["Sample images", "Upload your own"], horizontal=True)

    input_image = None

    if image_source == "Sample images":
        import os
        img_dir = os.path.join(os.path.dirname(__file__), 'images')
        available = sorted([f for f in os.listdir(img_dir)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        if available:
            selected = st.selectbox("Select sample image", available)
            img_path = os.path.join(img_dir, selected)
            raw = np.array(Image.open(img_path))
            st.image(raw, caption=f"Selected: {selected}", width=300)
            input_image = raw
        else:
            st.warning("No sample images found in ./images/")
    else:
        uploaded = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg', 'bmp'])
        if uploaded:
            raw = np.array(Image.open(uploaded))
            st.image(raw, caption="Uploaded image", width=300)
            input_image = raw

    if input_image is None:
        st.info("Please select or upload an image to begin.")
        st.stop()

    # --- Parameters ---
    st.header("2. Parameters")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        img_size_exp = st.selectbox(
            "Resize image to (2^n x 2^n)",
            [5, 6, 7, 8],
            index=1,
            format_func=lambda x: f"{2**x}x{2**x} ({2**x} pixels)"
        )
        img_size = 2 ** img_size_exp

    with col_p2:
        patch_qb = st.selectbox(
            "Patch qubits (per dimension)",
            [1, 2, 3],
            index=1,
            format_func=lambda x: f"{x} qubits -> {2**x}x{2**x} patch"
        )

    with col_p3:
        thr_ratio = st.slider("Threshold ratio", 0.1, 2.0, 0.7, 0.1)

    col_p4, col_p5 = st.columns(2)
    with col_p4:
        stride_mode = st.selectbox(
            "Boundary restoration",
            ["with_restoration", "without_restoration"],
            format_func=lambda x: "With Restoration (overlapping patches)" if x == "with_restoration"
                                  else "Without Restoration (non-overlapping)"
        )
    with col_p5:
        remove_noise = st.checkbox("Apply Gaussian blur (classical methods)", value=False)

    # Prepare image
    gray = load_image_from_array(input_image, resize=(img_size, img_size))

    # --- Run Edge Detection ---
    st.header("3. Results")

    tabs = st.tabs(["QHED (Quantum)", "Classical Methods", "Side-by-Side Comparison"])

    # ---- TAB 1: QHED ----
    with tabs[0]:
        st.subheader("Quantum Hadamard Edge Detection")

        patch_size = 2 ** patch_qb
        total_data_qubits = 2 * patch_qb
        total_qubits = total_data_qubits + 1

        n_patches_no_overlap = (img_size // patch_size) ** 2
        n_patches_overlap = ((img_size - 1) // (patch_size - 1)) ** 2 if patch_size > 1 else img_size ** 2

        st.markdown(f"""
        **Configuration:**
        - Image: {img_size}x{img_size} pixels
        - Patch: {patch_size}x{patch_size} pixels
        - Qubits per patch: {total_qubits} ({total_data_qubits} data + 1 ancilla)
        - Patches (no overlap): ~{n_patches_no_overlap}
        - Patches (with overlap): ~{n_patches_overlap}
        - Mode: {'With' if stride_mode == 'with_restoration' else 'Without'} Boundary Restoration
        """)

        if st.button("Run QHED", type="primary"):
            progress_bar = st.progress(0, text="Processing patches...")

            def update_progress(current, total):
                progress_bar.progress(current / total,
                                      text=f"Processing patch {current}/{total}...")

            start = time.time()
            result, n_patches = edge_detection_stride(
                gray,
                width_qb=patch_qb,
                thr_ratio=thr_ratio,
                stride_mode=stride_mode,
                patch_boundary_zero=True,
                progress_callback=update_progress,
            )
            elapsed = time.time() - start

            progress_bar.progress(1.0, text="Done!")

            st.success(f"Completed in {elapsed:.2f}s | {n_patches} patches processed")

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("**Original**")
                st.image(gray, clamp=True, width=400)
            with col_r2:
                st.markdown(f"**QHED Edge Detection ({'BR' if stride_mode == 'with_restoration' else 'No BR'})**")
                st.image(result.astype(float), clamp=True, width=400)

            # Store result in session state for comparison
            st.session_state['qhed_result'] = result
            st.session_state['qhed_time'] = elapsed
            st.session_state['qhed_gray'] = gray

            # Download
            st.download_button(
                "Download QHED result",
                img_to_bytes(result),
                file_name="qhed_result.png",
                mime="image/png",
            )

        # Show both modes comparison
        if st.button("Compare With vs Without Restoration"):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.markdown("**Original**")
                st.image(gray, clamp=True, width=300)

            progress1 = st.progress(0, text="Without restoration...")
            start1 = time.time()
            result_no_br, n1 = edge_detection_stride(
                gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                stride_mode='without_restoration',
                progress_callback=lambda c, t: progress1.progress(c/t, text=f"No BR: {c}/{t}")
            )
            time_no_br = time.time() - start1
            progress1.progress(1.0, text="Done (without restoration)")

            progress2 = st.progress(0, text="With restoration...")
            start2 = time.time()
            result_br, n2 = edge_detection_stride(
                gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                stride_mode='with_restoration',
                progress_callback=lambda c, t: progress2.progress(c/t, text=f"BR: {c}/{t}")
            )
            time_br = time.time() - start2
            progress2.progress(1.0, text="Done (with restoration)")

            with col_b:
                st.markdown(f"**Without Restoration** ({n1} patches, {time_no_br:.2f}s)")
                st.image(result_no_br.astype(float), clamp=True, width=300)
            with col_c:
                st.markdown(f"**With Restoration** ({n2} patches, {time_br:.2f}s)")
                st.image(result_br.astype(float), clamp=True, width=300)

            # Download comparison
            fig_comp, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(gray, cmap='gray'); axes[0].set_title('Original'); axes[0].axis('off')
            axes[1].imshow(result_no_br, cmap='gray'); axes[1].set_title(f'QHED w/o BR ({n1} patches)'); axes[1].axis('off')
            axes[2].imshow(result_br, cmap='gray'); axes[2].set_title(f'QHED w/ BR ({n2} patches)'); axes[2].axis('off')
            plt.tight_layout()
            st.download_button(
                "Download comparison image",
                fig_to_bytes(fig_comp, dpi=200),
                file_name="qhed_br_comparison.png",
                mime="image/png"
            )
            plt.close(fig_comp)

    # ---- TAB 2: Classical ----
    with tabs[1]:
        st.subheader("Classical Edge Detection Methods")

        methods = st.multiselect(
            "Select methods to run",
            ["Sobel", "Prewitt", "Laplacian", "Canny"],
            default=["Sobel", "Canny"]
        )

        col_canny1, col_canny2 = st.columns(2)
        with col_canny1:
            canny_thr1 = st.slider("Canny threshold 1", 0, 255, 50) if "Canny" in methods else 50
        with col_canny2:
            canny_thr2 = st.slider("Canny threshold 2", 0, 255, 200) if "Canny" in methods else 200

        sobel_ksize = 3
        if "Sobel" in methods:
            sobel_ksize = st.selectbox("Sobel kernel size", [3, 5, 7], index=0)

        if st.button("Run Classical Edge Detection", type="primary"):
            gray_u8 = (gray * 255).astype(np.uint8)

            results_classical = {}
            timings = {}

            for m in methods:
                start = time.time()
                if m == "Sobel":
                    results_classical[m] = sobel_edge_detection(gray_u8, kernel_size=sobel_ksize, remove_noise=remove_noise)
                elif m == "Prewitt":
                    results_classical[m] = prewitt_edge_detection(gray_u8, remove_noise=remove_noise)
                elif m == "Laplacian":
                    results_classical[m] = laplacian_edge_detection(gray_u8, remove_noise=remove_noise)
                elif m == "Canny":
                    results_classical[m] = canny_edge_detection(gray_u8, thr1=canny_thr1, thr2=canny_thr2, remove_noise=remove_noise)
                timings[m] = time.time() - start

            # Store for comparison
            st.session_state['classical_results'] = results_classical
            st.session_state['classical_timings'] = timings

            # Display
            n_methods = len(methods)
            cols = st.columns(min(n_methods + 1, 4))
            with cols[0]:
                st.markdown("**Original**")
                st.image(gray, clamp=True, width=250)

            for idx, m in enumerate(methods):
                with cols[(idx + 1) % len(cols)]:
                    st.markdown(f"**{m}** ({timings[m]*1000:.1f} ms)")
                    st.image(results_classical[m], clamp=True, width=250)

            # Download all
            n_total = n_methods + 1
            fig_cl, axes = plt.subplots(1, n_total, figsize=(5 * n_total, 5))
            axes[0].imshow(gray, cmap='gray'); axes[0].set_title('Original'); axes[0].axis('off')
            for idx, m in enumerate(methods):
                axes[idx+1].imshow(results_classical[m], cmap='gray')
                axes[idx+1].set_title(f'{m} ({timings[m]*1000:.1f}ms)')
                axes[idx+1].axis('off')
            plt.tight_layout()
            st.download_button(
                "Download classical results",
                fig_to_bytes(fig_cl, dpi=200),
                file_name="classical_edge_detection.png",
                mime="image/png"
            )
            plt.close(fig_cl)

    # ---- TAB 3: Comparison ----
    with tabs[2]:
        st.subheader("QHED vs Classical Edge Detection")
        st.markdown("""
        Run both QHED and classical methods first (in the other tabs), then come here to see
        the side-by-side comparison. Or click below to run everything at once.
        """)

        if st.button("Run Full Comparison", type="primary"):
            gray_u8 = (gray * 255).astype(np.uint8)
            all_results = {}
            all_times = {}

            # QHED
            progress = st.progress(0, text="Running QHED...")
            start = time.time()
            qhed_res, n_q = edge_detection_stride(
                gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                stride_mode=stride_mode,
                progress_callback=lambda c, t: progress.progress(c/t, text=f"QHED: {c}/{t}")
            )
            all_results['QHED'] = qhed_res.astype(float)
            all_times['QHED'] = time.time() - start
            progress.progress(1.0, text="QHED done")

            # Classical
            for name, func, kwargs in [
                ("Sobel", sobel_edge_detection, {"remove_noise": remove_noise}),
                ("Canny", canny_edge_detection, {"remove_noise": remove_noise}),
                ("Prewitt", prewitt_edge_detection, {"remove_noise": remove_noise}),
                ("Laplacian", laplacian_edge_detection, {"remove_noise": remove_noise}),
            ]:
                start = time.time()
                all_results[name] = func(gray_u8, **kwargs)
                all_times[name] = time.time() - start

            # Display
            n_total = len(all_results) + 1
            fig_all, axes = plt.subplots(1, n_total, figsize=(4 * n_total, 4))
            axes[0].imshow(gray, cmap='gray')
            axes[0].set_title('Original', fontsize=11)
            axes[0].axis('off')

            for idx, (name, result) in enumerate(all_results.items()):
                axes[idx+1].imshow(result, cmap='gray')
                t_str = f"{all_times[name]*1000:.1f}ms" if all_times[name] < 1 else f"{all_times[name]:.2f}s"
                axes[idx+1].set_title(f'{name}\n({t_str})', fontsize=11)
                axes[idx+1].axis('off')
            plt.tight_layout()
            st.pyplot(fig_all)

            st.download_button(
                "Download full comparison",
                fig_to_bytes(fig_all, dpi=200),
                file_name="full_comparison.png",
                mime="image/png"
            )
            plt.close(fig_all)

            # Timing table
            st.markdown("### Execution Time Comparison")
            timing_data = {k: f"{v*1000:.1f} ms" if v < 1 else f"{v:.2f} s"
                          for k, v in all_times.items()}
            st.table(timing_data)

            st.session_state['qhed_result'] = qhed_res
            st.session_state['qhed_time'] = all_times['QHED']
            st.session_state['qhed_gray'] = gray


# ===================================================================
# PAGE 4: Complexity Comparison
# ===================================================================
elif page == "4. Complexity Comparison":
    st.title("Computational Complexity: QHED vs Classical")

    st.header("Theoretical Complexity")

    st.markdown("""
    | Method | Type | Time Complexity | Space (Memory) |
    |--------|------|-----------------|----------------|
    | Sobel / Prewitt | Classical | O(n^2) per kernel | O(n^2) pixels |
    | Canny | Classical | O(n^2) multi-stage | O(n^2) pixels |
    | Laplacian | Classical | O(n^2) | O(n^2) pixels |
    | **QHED** | **Quantum** | **O(n^2) encoding + O(1) detection** | **O(log n) qubits** |
    | **QHED-BR** | **Quantum** | **O(n^2) encoding + Q*O(1) detection** | **O(log n) qubits** |

    Where:
    - **n** = image side length (total pixels = n^2)
    - **Q** = number of patches
    - QHED requires only **ceil(log2(n^2)) + 1** qubits
    """)

    st.header("Patch Count Analysis")

    st.markdown("See how many patches are needed for different image sizes and qubit counts:")

    col1, col2 = st.columns(2)
    with col1:
        sizes = [2**i for i in range(4, 11)]  # 16 to 1024
        qubits_options = [1, 2, 3, 4, 5]

        fig, ax = plt.subplots(figsize=(8, 5))
        for qb in qubits_options:
            patch = 2 ** qb
            patches_no_br = [(s // patch) ** 2 if s >= patch else 1 for s in sizes]
            patches_br = [((s - 1) // (patch - 1)) ** 2 if s >= patch and patch > 1 else s**2 for s in sizes]
            ax.plot(sizes, patches_br, 'o-', label=f'{qb} qb/dim ({patch}x{patch} patch, BR)', linewidth=2)

        ax.set_xlabel('Image side length (pixels)', fontsize=12)
        ax.set_ylabel('Number of patches', fontsize=12)
        ax.set_title('Patches Required vs Image Size (with BR)', fontsize=13)
        ax.legend(fontsize=9)
        ax.set_yscale('log')
        ax.set_xscale('log', base=2)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        for qb in [2, 3, 4]:
            patch = 2 ** qb
            patches_no_br = [(s // patch) ** 2 if s >= patch else 1 for s in sizes]
            patches_br = [((s - 1) // (patch - 1)) ** 2 if s >= patch and patch > 1 else s**2 for s in sizes]
            ax2.plot(sizes, patches_no_br, 's--', label=f'{qb} qb w/o BR', alpha=0.7)
            ax2.plot(sizes, patches_br, 'o-', label=f'{qb} qb w/ BR', linewidth=2)

        ax2.set_xlabel('Image side length (pixels)', fontsize=12)
        ax2.set_ylabel('Number of patches', fontsize=12)
        ax2.set_title('BR vs No-BR Patch Count', fontsize=13)
        ax2.legend(fontsize=9)
        ax2.set_yscale('log')
        ax2.set_xscale('log', base=2)
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
        plt.close(fig2)

    st.header("Quantum Advantage: Memory Efficiency")

    st.markdown("""
    The key quantum advantage lies in **exponential memory compression**:

    | Image Size | Pixels | Classical Memory | Quantum Qubits |
    |-----------|--------|-----------------|----------------|
    | 4x4 | 16 | 16 values | 4 + 1 = **5** |
    | 8x8 | 64 | 64 values | 6 + 1 = **7** |
    | 16x16 | 256 | 256 values | 8 + 1 = **9** |
    | 32x32 | 1024 | 1024 values | 10 + 1 = **11** |
    | 64x64 | 4096 | 4096 values | 12 + 1 = **13** |
    | 256x256 | 65536 | 65536 values | 16 + 1 = **17** |
    """)

    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 5))

    img_sides = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
    classical_mem = [s*s for s in img_sides]
    quantum_qubits = [int(np.ceil(np.log2(s*s))) + 1 for s in img_sides]

    ax3a.plot(img_sides, classical_mem, 'ro-', label='Classical (pixels)', linewidth=2, markersize=8)
    ax3a.plot(img_sides, quantum_qubits, 'bs-', label='Quantum (qubits)', linewidth=2, markersize=8)
    ax3a.set_xlabel('Image side length')
    ax3a.set_ylabel('Memory units')
    ax3a.set_title('Memory: Classical vs Quantum')
    ax3a.set_yscale('log')
    ax3a.set_xscale('log', base=2)
    ax3a.legend()
    ax3a.grid(True, alpha=0.3)

    # Classical complexity O(n^2) vs Quantum O(1) per patch
    n_values = np.array(img_sides)
    classical_ops = n_values ** 2  # O(n^2) for gradient-based
    # Quantum: encoding O(n^2) + detection O(1) -- but per-patch it's O(1) detection
    quantum_detection = np.ones_like(n_values)  # O(1) per patch

    ax3b.plot(n_values, classical_ops, 'ro-', label='Classical edge detection O(n^2)', linewidth=2)
    ax3b.plot(n_values, quantum_detection, 'bs-', label='QHED detection per patch O(1)', linewidth=2)
    ax3b.set_xlabel('Image side length')
    ax3b.set_ylabel('Operations')
    ax3b.set_title('Edge Detection Complexity (per operation)')
    ax3b.set_yscale('log')
    ax3b.set_xscale('log', base=2)
    ax3b.legend()
    ax3b.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.header("NISQ Era Context")
    st.markdown("""
    In the current NISQ (Noisy Intermediate-Scale Quantum) era:

    - **Available qubits:** IBM's most advanced processors have ~1000+ qubits, but with significant noise
    - **Practical qubits:** For reliable computation, effectively far fewer qubits are usable
    - **QHED-BR significance:** Even with just 5-13 qubits, we can process arbitrarily large images
      by using the patch-based approach with boundary restoration
    - **Polynomial overhead:** The boundary restoration only adds polynomial (not exponential) computation

    This makes QHED-BR a **practical quantum algorithm for the NISQ era** -- it demonstrates
    quantum advantage in memory efficiency while working within the constraints of current hardware.
    """)

    st.markdown("---")
    st.markdown("""
    **References:**
    - [Qiskit - Open-source quantum computing SDK](https://qiskit.org/)
    - [IBM Quantum Computing](https://quantum-computing.ibm.com/)
    - Yao et al., "Quantum image processing and its application to edge detection," Physical Review X 7.3 (2017)
    """)
