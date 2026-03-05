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
            list(range(1, 6)),
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
        try:
            fig = qc.draw('mpl', fold=-1)
            st.pyplot(fig)
            st.download_button(
                "Download circuit diagram",
                fig_to_bytes(fig),
                file_name="qhed_circuit.png",
                mime="image/png"
            )
            plt.close(fig)
        except Exception:
            # Fallback to text drawing if pylatexenc is not installed
            circuit_text = qc.draw('text', fold=120)
            st.code(str(circuit_text), language=None)
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
        img_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
        # Collect images from root and all subdirectories
        available = []
        for root, _dirs, files in os.walk(img_dir):
            for f in sorted(files):
                if f.lower().endswith(img_extensions):
                    rel = os.path.relpath(os.path.join(root, f), img_dir)
                    available.append(rel)
        available.sort()
        if available:
            selected = st.selectbox("Select sample image", available)
            img_path = os.path.join(img_dir, selected)
            raw = np.array(Image.open(img_path))
            st.image(raw, caption=f"Selected: {selected}", width=300)
            input_image = raw
        else:
            st.warning("No sample images found in ./images/ (including subdirectories)")
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
            list(range(4, 10)),
            index=2,
            format_func=lambda x: f"{2**x}x{2**x} ({2**(2*x):,} pixels)"
        )
        img_size = 2 ** img_size_exp

    with col_p2:
        # Min 3 qb/dim (8x8 patch), max capped by image size and 8 (256x256 = 17 qubits)
        max_patch_qb = min(img_size_exp, 8)
        min_patch_qb = 3  # minimum 8x8 patches
        patch_qb_options = list(range(min_patch_qb, max_patch_qb + 1))
        if not patch_qb_options:
            st.error(f"Image too small for minimum patch size (8x8). Increase image size to at least 16x16.")
            st.stop()
        default_idx = len(patch_qb_options) - 1  # default to maximum qubits
        patch_qb = st.selectbox(
            "Patch qubits (per dimension)",
            patch_qb_options,
            index=default_idx,
            format_func=lambda x: f"{x} qb/dim -> {2**x}x{2**x} patch ({2*x}+1 = {2*x+1} total qubits)"
        )

    with col_p3:
        thr_ratio = st.slider("Threshold ratio", 0.1, 2.0, 0.7, 0.1)

    if patch_qb >= 5:
        est_patch_size = 2 ** patch_qb
        est_total_qb = 2 * patch_qb + 1
        st.warning(
            f"Large patch size: {est_patch_size}x{est_patch_size} pixels per patch "
            f"({est_total_qb} qubits). Statevector simulation operates on a "
            f"2^{est_total_qb} = {2**est_total_qb:,} dimensional vector per patch. "
            f"This may be slow for large images."
        )

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
        br_stride = max(patch_size - 2, 1)
        n_patches_overlap = int(np.ceil((img_size - 2) / br_stride)) ** 2 if patch_size > 2 else img_size ** 2

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

    # ------------------------------------------------------------------
    # Section 1: Notation & Setup
    # ------------------------------------------------------------------
    st.header("1. Notation and Setup")
    st.markdown(r"""
    We compare the computational complexity of QHED (with and without Boundary Restoration)
    against classical edge detection methods (Sobel, Prewitt, Laplacian, Canny).

    | Symbol | Definition |
    |--------|-----------|
    | $N$ | Image side length ($N \times N$ image, total $N^2$ pixels) |
    | $p = 2^k$ | Patch side length ($p \times p$ patch, total $p^2$ pixels) |
    | $k$ | Number of qubits per spatial dimension |
    | $q = 2k + 1$ | Total qubits per QHED circuit ($2k$ data qubits + 1 ancilla) |
    | $Q$ | Number of patches to process the full image |
    | $s$ | Stride (step size between adjacent patches) |

    **Patch counts:**

    $$Q_{\text{no-BR}} = \left\lceil \frac{N}{p} \right\rceil^2 \quad(\text{stride } s = p, \text{ no overlap})$$

    $$Q_{\text{BR}} = \left\lceil \frac{N - 2}{p - 2} \right\rceil^2 \quad(\text{stride } s = p - 2, \text{ 2-pixel overlap with boundary zeroing})$$
    """)

    # ------------------------------------------------------------------
    # Section 2: Operation breakdown per patch
    # ------------------------------------------------------------------
    st.header("2. QHED Circuit: Per-Patch Operation Breakdown")
    st.markdown(r"""
    Each QHED patch goes through three stages. Understanding these separately is critical
    for an honest complexity comparison.

    ---

    **Stage 1 -- Amplitude Encoding (Classical $\to$ Quantum)**

    The image patch is encoded into the amplitudes of a quantum state:

    $$|\psi\rangle = \sum_{i=0}^{p^2 - 1} a_i |i\rangle, \quad \text{where } \sum |a_i|^2 = 1$$

    Preparing an arbitrary $m$-qubit state requires $O(2^m)$ CNOT gates
    (Shende, Bullock & Markov, 2006). Here $m = 2k$, so:

    $$T_{\text{encode}} = O(2^{2k}) = O(p^2) \text{ quantum gates per patch}$$

    This is run twice (horizontal and vertical scans), giving $2 \times O(p^2)$ total.

    ---

    **Stage 2 -- Quantum Edge Detection (the "detection" step)**

    The core quantum circuit consists of:

    | Operation | Gate count |
    |-----------|-----------|
    | Hadamard on ancilla | $O(1)$ |
    | $D_{2n-1}$: cyclic-shift (increment-by-1) on $q$ qubits | $O(q) = O(\log p^2)$ |
    | Hadamard on ancilla | $O(1)$ |

    The permutation unitary $D_{2n-1}$ maps $|x\rangle \to |x + 1 \bmod 2^q\rangle$.
    This is an **adder circuit** implementable with a cascade of $O(q)$ Toffoli gates
    (Draper, 2000; Cuccaro et al., 2004):

    $$T_{\text{detect}} = O(q) = O(2k + 1) = O(\log p^2) \text{ quantum gates per patch}$$

    This is the step where quantum parallelism provides its advantage: a single quantum
    circuit computes all $p^2$ pixel differences simultaneously.

    ---

    **Stage 3 -- Readout / Decoding (Quantum $\to$ Classical)**

    - **Statevector simulation**: Extract $2^q$ amplitudes, select odd-indexed entries $\to O(p^2)$
    - **Shot-based (QASM)**: Repeat measurement $S$ times, process counts $\to O(S \cdot p^2)$
    - **Thresholding**: Compare each pixel against threshold $\to O(p^2)$

    $$T_{\text{readout}} = O(p^2) \text{ classical operations per patch}$$

    ---

    **Summary per patch (run twice for H/V scans):**

    | Stage | Operations | Type |
    |-------|-----------|------|
    | Encoding | $O(p^2)$ | Quantum gates |
    | Detection | $O(\log p^2)$ | Quantum gates |
    | Readout | $O(p^2)$ | Classical ops |
    | **Total** | **$O(p^2)$** | **Dominated by encoding** |
    """)

    # ------------------------------------------------------------------
    # Section 3: Classical methods
    # ------------------------------------------------------------------
    st.header("3. Classical Edge Detection Complexity")
    st.markdown(r"""
    Classical methods apply convolution kernels directly on the $N \times N$ image.

    | Method | Kernel | Ops/pixel | Total Time | Space |
    |--------|--------|-----------|-----------|-------|
    | **Sobel** | Two $3 \times 3$ kernels ($G_x, G_y$) | $\sim 2 \times (9 \text{ mult} + 8 \text{ add}) + \text{combine} \approx 38$ | $O(N^2)$ | $O(N^2)$ |
    | **Prewitt** | Two $3 \times 3$ kernels | $\sim 38$ | $O(N^2)$ | $O(N^2)$ |
    | **Laplacian** | One $3 \times 3$ kernel | $\sim 9 \text{ mult} + 8 \text{ add} = 17$ | $O(N^2)$ | $O(N^2)$ |
    | **Canny** | Gaussian blur + gradient + NMS + hysteresis | $\sim 4 \times O(N^2)$ | $O(N^2)$ | $O(N^2)$ |

    All classical methods have:

    $$T_{\text{classical}} = c_{\text{cl}} \cdot N^2, \quad S_{\text{classical}} = O(N^2)$$

    where $c_{\text{cl}}$ is a constant depending on the method (Sobel $\approx 38$, Canny $\approx 100+$).
    """)

    # ------------------------------------------------------------------
    # Section 4: Case 1 - Detection only
    # ------------------------------------------------------------------
    st.header("4. Case 1: Quantum Detection Only (Excluding Encoding/Decoding)")
    st.markdown(r"""
    If we assume quantum data is **already encoded** in quantum memory (e.g., via QRAM)
    and focus purely on the edge detection operation itself, we can isolate the
    quantum advantage most clearly.

    **Per patch:** $T_{\text{detect}} = O(\log p^2) = O(k)$

    **Full image (with BR):**

    $$T_{\text{QHED}}^{(\text{detect})} = Q_{\text{BR}} \times O(\log p^2) = \left\lceil \frac{N-2}{p-2} \right\rceil^2 \times O(k)$$

    For large $N \gg p$, this simplifies to:

    $$T_{\text{QHED}}^{(\text{detect})} \approx \frac{N^2}{(p-2)^2} \cdot O(\log p^2)$$

    **Speedup over classical:**

    $$\text{Speedup} = \frac{T_{\text{classical}}}{T_{\text{QHED}}^{(\text{detect})}}
    = \frac{c_{\text{cl}} \cdot N^2}{\frac{N^2}{(p-2)^2} \cdot c_q \cdot \log p^2}
    = \frac{c_{\text{cl}}}{c_q} \cdot \frac{(p-2)^2}{\log p^2}$$

    Key observation: **the speedup is independent of $N$** and grows as $\Theta\!\left(\frac{p^2}{\log p}\right)$ with patch size.

    | $k$ (qubits/dim) | $p$ (patch) | $(p-2)^2$ | $\log_2 p^2$ | Speedup factor $\propto \frac{(p-2)^2}{\log_2 p^2}$ |
    |---|---|---|---|---|
    | 2 | 4 | 4 | 4 | 1.0 |
    | 3 | 8 | 36 | 6 | 6.0 |
    | 4 | 16 | 196 | 8 | 24.5 |
    | 5 | 32 | 900 | 10 | 90.0 |
    | 6 | 64 | 3844 | 12 | 320.3 |
    | 7 | 128 | 15876 | 14 | 1134.0 |

    The quantum advantage grows **super-linearly** with patch size. Even with the modest
    $p = 4$ ($k = 2$), quantum detection matches classical per-pixel cost; at $p = 16$ ($k = 4$),
    it is ~25x faster; at $p = 64$ ($k = 6$), ~320x faster.
    """)

    # --- Graph: Case 1 ---
    st.subheader("Case 1 Visualization: Detection-Only Complexity")

    sizes = np.array([2**i for i in range(4, 12)])  # 16 to 2048
    c_cl = 38  # Sobel ops per pixel

    fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Total operations vs image size for different k
    for k in [2, 3, 4, 5, 6]:
        p = 2 ** k
        q = 2 * k + 1
        stride = max(p - 2, 1)
        Q_br = np.array([int(np.ceil((s - 2) / stride)) ** 2 if s >= p else 1 for s in sizes])
        ops_detect = Q_br * q  # O(q) gates per patch
        ax1a.plot(sizes, ops_detect, 'o-', label=f'QHED k={k} (p={p})', linewidth=2, markersize=5)

    classical_ops = c_cl * sizes ** 2
    ax1a.plot(sizes, classical_ops, 'k^--', label='Sobel (~38 ops/px)', linewidth=2.5, markersize=7)

    ax1a.set_xlabel('Image side length N', fontsize=12)
    ax1a.set_ylabel('Total operations (gates / ops)', fontsize=12)
    ax1a.set_title('Case 1: Detection-Only Operations', fontsize=13)
    ax1a.set_yscale('log')
    ax1a.set_xscale('log', base=2)
    ax1a.legend(fontsize=9)
    ax1a.grid(True, alpha=0.3)

    # Right: Speedup factor vs patch size
    k_range = np.arange(2, 9)
    p_range = 2 ** k_range
    speedup = (p_range - 2) ** 2 / (2 * np.log2(p_range ** 2))  # normalized
    ax1b.bar(k_range, speedup, color=['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#00BCD4', '#795548'],
             edgecolor='black', linewidth=0.5)
    for i, (ki, sp) in enumerate(zip(k_range, speedup)):
        ax1b.text(ki, sp * 1.05, f'{sp:.1f}x', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1b.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax1b.set_ylabel('Speedup factor (p-2)^2 / log(p^2)', fontsize=12)
    ax1b.set_title('Quantum Speedup vs Patch Size (Detection Only)', fontsize=13)
    ax1b.set_xticks(k_range)
    ax1b.set_xticklabels([f'k={k}\np={2**k}' for k in k_range], fontsize=9)
    ax1b.set_yscale('log')
    ax1b.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    # ------------------------------------------------------------------
    # Section 5: Case 2 - End-to-end
    # ------------------------------------------------------------------
    st.header("5. Case 2: End-to-End (Including Encoding & Decoding)")
    st.markdown(r"""
    In practice, classical data must be loaded into the quantum computer and results
    must be read back. This encoding/decoding overhead dominates the total cost.

    **Per patch (×2 for H/V scans):**

    $$T_{\text{patch}}^{(\text{total})} = \underbrace{O(p^2)}_{\text{encode}} + \underbrace{O(\log p^2)}_{\text{detect}} + \underbrace{O(p^2)}_{\text{readout}} = O(p^2)$$

    **Full image (with BR):**

    $$T_{\text{QHED}}^{(\text{e2e})} = Q_{\text{BR}} \times O(p^2)
    = \left\lceil \frac{N-2}{p-2} \right\rceil^2 \times c_q' \cdot p^2$$

    For large $N \gg p$:

    $$T_{\text{QHED}}^{(\text{e2e})} \approx N^2 \cdot \frac{c_q' \cdot p^2}{(p-2)^2}
    = c_q' \cdot N^2 \cdot \left(\frac{p}{p-2}\right)^2$$

    **Comparison with classical:**

    $$\frac{T_{\text{QHED}}^{(\text{e2e})}}{T_{\text{classical}}} \approx \frac{c_q'}{c_{\text{cl}}} \cdot \left(\frac{p}{p-2}\right)^2$$

    | $k$ | $p$ | $(p/(p-2))^2$ | Overhead factor |
    |-----|-----|---------------|-----------------|
    | 2 | 4 | 4.00 | $4.00 \cdot c_q'/c_{\text{cl}}$ |
    | 3 | 8 | 1.78 | $1.78 \cdot c_q'/c_{\text{cl}}$ |
    | 4 | 16 | 1.31 | $1.31 \cdot c_q'/c_{\text{cl}}$ |
    | 5 | 32 | 1.13 | $1.13 \cdot c_q'/c_{\text{cl}}$ |
    | 6 | 64 | 1.06 | $1.06 \cdot c_q'/c_{\text{cl}}$ |
    | $\to \infty$ | $\to \infty$ | $\to 1.00$ | $c_q'/c_{\text{cl}}$ |

    **Key insight:** When encoding is included, QHED and classical methods are both $O(N^2)$.
    The asymptotic time complexity is the **same**. The overhead factor $(p/(p-2))^2$ converges
    to 1 as $p$ grows. Whether QHED is actually faster depends on the constant factor ratio
    $c_q'/c_{\text{cl}}$, which is **hardware-dependent**.

    In current NISQ-era hardware, quantum gate operations are orders of magnitude slower
    than classical FLOPs, so $c_q' \gg c_{\text{cl}}$ and classical methods are faster in wall-clock time.
    However, as quantum hardware matures and gate speeds improve, the constants will become comparable.
    """)

    # --- Graph: Case 2 ---
    st.subheader("Case 2 Visualization: End-to-End Complexity")

    fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Total operations vs N for different k
    for k in [2, 3, 4, 5, 6]:
        p = 2 ** k
        stride = max(p - 2, 1)
        Q_br = np.array([int(np.ceil((s - 2) / stride)) ** 2 if s >= p else 1 for s in sizes])
        ops_e2e = Q_br * (2 * p * p)  # encode + readout dominated, ×2 for H/V
        ax2a.plot(sizes, ops_e2e, 'o-', label=f'QHED k={k} (p={p})', linewidth=2, markersize=5)

    classical_ops = c_cl * sizes ** 2
    ax2a.plot(sizes, classical_ops, 'k^--', label='Sobel (~38 ops/px)', linewidth=2.5, markersize=7)

    canny_ops = 120 * sizes ** 2
    ax2a.plot(sizes, canny_ops, 'ks--', label='Canny (~120 ops/px)', linewidth=2, markersize=5, alpha=0.6)

    ax2a.set_xlabel('Image side length N', fontsize=12)
    ax2a.set_ylabel('Total operations', fontsize=12)
    ax2a.set_title('Case 2: End-to-End Operations', fontsize=13)
    ax2a.set_yscale('log')
    ax2a.set_xscale('log', base=2)
    ax2a.legend(fontsize=8)
    ax2a.grid(True, alpha=0.3)

    # Right: Overhead factor (p/(p-2))^2 vs k
    k_range2 = np.arange(2, 9)
    p_range2 = 2.0 ** k_range2
    overhead = (p_range2 / (p_range2 - 2)) ** 2
    colors2 = ['#F44336', '#FF9800', '#4CAF50', '#2196F3', '#9C27B0', '#00BCD4', '#795548']
    ax2b.bar(k_range2, overhead, color=colors2, edgecolor='black', linewidth=0.5)
    ax2b.axhline(y=1.0, color='gray', linestyle='--', linewidth=1.5, label='Classical baseline (1.0x)')
    for i, (ki, oh) in enumerate(zip(k_range2, overhead)):
        ax2b.text(ki, oh + 0.05, f'{oh:.2f}x', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2b.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax2b.set_ylabel('Overhead factor (p/(p-2))^2', fontsize=12)
    ax2b.set_title('BR Overhead Factor (converges to 1.0)', fontsize=13)
    ax2b.set_xticks(k_range2)
    ax2b.set_xticklabels([f'k={k}\np={2**k}' for k in k_range2], fontsize=9)
    ax2b.legend(fontsize=10)
    ax2b.grid(True, alpha=0.3, axis='y')
    ax2b.set_ylim(0.8, max(overhead) + 0.5)

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # ------------------------------------------------------------------
    # Section 6: Space complexity
    # ------------------------------------------------------------------
    st.header("6. Space Complexity: Exponential Memory Advantage")
    st.markdown(r"""
    Regardless of encoding overhead, QHED achieves an **exponential advantage in space (memory)**:

    | Resource | Classical | QHED |
    |----------|----------|------|
    | **Per patch** | $O(p^2)$ values in memory | $O(\log p^2) = O(k)$ qubits |
    | **Per image** | $O(N^2)$ values simultaneously | $O(k)$ qubits (patches processed sequentially) |

    A $p \times p = 2^k \times 2^k$ patch requires:
    - **Classical:** $p^2 = 2^{2k}$ memory cells
    - **Quantum:** $2k + 1$ qubits

    This is an **exponential compression**: $2^{2k}$ classical values $\to$ $2k + 1$ qubits.

    | Patch size | Pixels | Classical Memory | Quantum Qubits | Compression ratio |
    |-----------|--------|-----------------|----------------|-------------------|
    | $4 \times 4$ | 16 | 16 values | **5** qubits | 3.2x |
    | $8 \times 8$ | 64 | 64 values | **7** qubits | 9.1x |
    | $16 \times 16$ | 256 | 256 values | **9** qubits | 28.4x |
    | $32 \times 32$ | 1024 | 1024 values | **11** qubits | 93.1x |
    | $64 \times 64$ | 4096 | 4096 values | **13** qubits | 315.1x |
    | $128 \times 128$ | 16384 | 16384 values | **15** qubits | 1092.3x |
    | $256 \times 256$ | 65536 | 65536 values | **17** qubits | 3855.1x |
    """)

    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 5.5))

    k_vals = np.arange(1, 10)
    p_vals = 2 ** k_vals
    classical_mem = p_vals ** 2
    quantum_mem = 2 * k_vals + 1
    compression = classical_mem / quantum_mem

    ax3a.semilogy(k_vals, classical_mem, 'ro-', label='Classical: $p^2 = 2^{2k}$', linewidth=2.5, markersize=8)
    ax3a.semilogy(k_vals, quantum_mem, 'bs-', label='Quantum: $2k+1$', linewidth=2.5, markersize=8)
    ax3a.fill_between(k_vals, quantum_mem, classical_mem, alpha=0.15, color='green',
                       label='Exponential gap')
    ax3a.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax3a.set_ylabel('Memory units', fontsize=12)
    ax3a.set_title('Space: Classical vs Quantum', fontsize=13)
    ax3a.legend(fontsize=10)
    ax3a.grid(True, alpha=0.3)
    ax3a.set_xticks(k_vals)
    ax3a.set_xticklabels([f'{k}\n({2**k}x{2**k})' for k in k_vals], fontsize=8)

    ax3b.bar(k_vals, compression, color='#4CAF50', edgecolor='black', linewidth=0.5)
    for ki, cr in zip(k_vals, compression):
        ax3b.text(ki, cr * 1.1, f'{cr:.0f}x', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax3b.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax3b.set_ylabel('Compression ratio ($p^2 / (2k+1)$)', fontsize=12)
    ax3b.set_title('Memory Compression Ratio', fontsize=13)
    ax3b.set_yscale('log')
    ax3b.grid(True, alpha=0.3, axis='y')
    ax3b.set_xticks(k_vals)
    ax3b.set_xticklabels([f'k={k}\np={2**k}' for k in k_vals], fontsize=8)

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    # ------------------------------------------------------------------
    # Section 7: Patch count analysis
    # ------------------------------------------------------------------
    st.header("7. Patch Count: BR vs No-BR")
    st.markdown(r"""
    Boundary Restoration increases the number of patches due to overlap.
    The additional cost is **polynomial** (not exponential):

    $$\frac{Q_{\text{BR}}}{Q_{\text{no-BR}}} = \left(\frac{p}{p-2}\right)^2 \xrightarrow{p \to \infty} 1$$
    """)

    col1, col2 = st.columns(2)
    sizes_plot = [2**i for i in range(4, 11)]

    with col1:
        fig4a, ax4a = plt.subplots(figsize=(8, 5))
        for qb in [3, 4, 5, 6]:
            patch = 2 ** qb
            br_stride = max(patch - 2, 1)
            patches_br = [int(np.ceil((s - 2) / br_stride)) ** 2 if s >= patch else 1 for s in sizes_plot]
            ax4a.plot(sizes_plot, patches_br, 'o-', label=f'k={qb} ({patch}x{patch})', linewidth=2)

        ax4a.set_xlabel('Image side length N', fontsize=12)
        ax4a.set_ylabel('Number of patches (Q)', fontsize=12)
        ax4a.set_title('Patches Required with BR', fontsize=13)
        ax4a.legend(fontsize=10)
        ax4a.set_yscale('log')
        ax4a.set_xscale('log', base=2)
        ax4a.grid(True, alpha=0.3)
        st.pyplot(fig4a)
        plt.close(fig4a)

    with col2:
        fig4b, ax4b = plt.subplots(figsize=(8, 5))
        for qb in [3, 4, 5]:
            patch = 2 ** qb
            patches_no = [int(np.ceil(s / patch)) ** 2 if s >= patch else 1 for s in sizes_plot]
            br_stride = max(patch - 2, 1)
            patches_br = [int(np.ceil((s - 2) / br_stride)) ** 2 if s >= patch else 1 for s in sizes_plot]
            ax4b.plot(sizes_plot, patches_no, 's--', label=f'k={qb} w/o BR', alpha=0.7)
            ax4b.plot(sizes_plot, patches_br, 'o-', label=f'k={qb} w/ BR', linewidth=2)

        ax4b.set_xlabel('Image side length N', fontsize=12)
        ax4b.set_ylabel('Number of patches (Q)', fontsize=12)
        ax4b.set_title('BR vs No-BR Patch Count', fontsize=13)
        ax4b.legend(fontsize=9)
        ax4b.set_yscale('log')
        ax4b.set_xscale('log', base=2)
        ax4b.grid(True, alpha=0.3)
        st.pyplot(fig4b)
        plt.close(fig4b)

    # ------------------------------------------------------------------
    # Section 8: Crossover analysis
    # ------------------------------------------------------------------
    st.header("8. Crossover Analysis: When Does Quantum Beat Classical?")
    st.markdown(r"""
    We identify two distinct crossover boundaries:

    ---

    ### Crossover A: Detection-Only Regime

    For quantum detection to beat classical edge detection:

    $$Q_{\text{BR}} \cdot O(\log p^2) < c_{\text{cl}} \cdot N^2$$

    Since $Q_{\text{BR}} \approx N^2/(p-2)^2$:

    $$\frac{N^2 \cdot \log p^2}{(p-2)^2} < c_{\text{cl}} \cdot N^2
    \implies \frac{\log p^2}{(p-2)^2} < c_{\text{cl}}$$

    For Sobel ($c_{\text{cl}} \approx 38$):
    - At $p = 4$ ($k=2$): $\log_2 16 / 4 = 1.0 < 38$ **-- satisfied**

    **Conclusion:** In the detection-only regime, QHED is advantageous for **all practical
    patch sizes** ($p \geq 4$). The advantage grows as $\Theta(p^2 / \log p)$.

    ---

    ### Crossover B: End-to-End Regime

    For the full pipeline including encoding:

    $$Q_{\text{BR}} \cdot c_q' \cdot p^2 < c_{\text{cl}} \cdot N^2$$

    $$\frac{c_q' \cdot p^2}{(p-2)^2} < c_{\text{cl}}
    \implies c_q' < c_{\text{cl}} \cdot \left(\frac{p-2}{p}\right)^2$$

    For large $p$, this becomes $c_q' < c_{\text{cl}}$. The crossover depends entirely
    on the **hardware constant ratio** $c_q' / c_{\text{cl}}$:

    - **Current NISQ era:** A single quantum gate takes ~10-1000 ns, while a classical FLOP
      takes ~0.1-1 ns. So $c_q' / c_{\text{cl}} \approx 10$--$10^4$. **Classical wins.**
    - **Fault-tolerant era:** With error-corrected qubits and faster gates,
      $c_q'$ is expected to approach $c_{\text{cl}}$. **Quantum becomes competitive.**
    - **With QRAM:** If QRAM provides $O(\log p^2)$ encoding (speculative), the end-to-end
      complexity drops to $Q \cdot O(\log p^2)$, recovering Case 1's advantage.

    ---

    ### Summary of Advantages

    | Dimension | Classical | QHED | Advantage |
    |-----------|----------|------|-----------|
    | **Time (detection only)** | $O(N^2)$ | $O\!\left(\frac{N^2 \log p}{p^2}\right)$ | Quantum: $\Theta(p^2/\log p)$ speedup |
    | **Time (end-to-end)** | $O(N^2)$ | $O(N^2)$ | **Same asymptotic** -- hardware-dependent |
    | **Space** | $O(N^2)$ or $O(p^2)$/patch | $O(\log p)$ qubits | Quantum: **exponential** advantage |
    | **BR overhead** | N/A | $(p/(p-2))^2 \to 1$ | Polynomial, vanishes for large $p$ |
    """)

    # --- Graph: Crossover ---
    st.subheader("Crossover Visualization")

    fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: End-to-end break-even as function of c_q'/c_cl ratio
    k_cross = np.arange(2, 9)
    p_cross = 2.0 ** k_cross
    max_cq_ratio = c_cl * ((p_cross - 2) / p_cross) ** 2  # max c_q' for quantum to win

    ax5a.bar(k_cross, max_cq_ratio, color='#2196F3', edgecolor='black', linewidth=0.5)
    ax5a.axhline(y=1, color='red', linestyle='--', linewidth=2, label="$c_q'/c_{cl} = 1$ (equal speed)")
    ax5a.axhline(y=0.1, color='orange', linestyle=':', linewidth=2, label="$c_q'/c_{cl} = 0.1$ (10x faster gates)")
    for ki, mv in zip(k_cross, max_cq_ratio):
        ax5a.text(ki, mv + 0.5, f'{mv:.1f}', ha='center', va='bottom', fontsize=9)
    ax5a.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax5a.set_ylabel(r"Maximum $c_q'$ for quantum advantage", fontsize=12)
    ax5a.set_title('End-to-End Break-Even Threshold\n(vs Sobel, $c_{cl}=38$)', fontsize=12)
    ax5a.set_xticks(k_cross)
    ax5a.set_xticklabels([f'k={k}\np={2**k}' for k in k_cross], fontsize=9)
    ax5a.legend(fontsize=9)
    ax5a.grid(True, alpha=0.3, axis='y')

    # Right: Three regimes on one plot
    N_range = np.logspace(np.log10(16), np.log10(4096), 100)
    k_example = 4  # p=16
    p_ex = 16
    q_ex = 2 * k_example + 1
    stride_ex = p_ex - 2

    Q_br_ex = np.ceil((N_range - 2) / stride_ex) ** 2
    detect_only = Q_br_ex * q_ex
    e2e_unit = Q_br_ex * 2 * p_ex ** 2  # c_q'=1 (unit gate cost)
    classical_sobel = 38 * N_range ** 2

    ax5b.loglog(N_range, classical_sobel, 'k-', label='Classical (Sobel)', linewidth=2.5)
    ax5b.loglog(N_range, detect_only, 'b-', label='QHED: detection only', linewidth=2)
    ax5b.loglog(N_range, e2e_unit, 'r--', label='QHED: end-to-end ($c_q\'=1$)', linewidth=2)
    ax5b.loglog(N_range, e2e_unit * 10, 'r:', label='QHED: end-to-end ($c_q\'=10$)', linewidth=2, alpha=0.7)

    ax5b.fill_between(N_range, detect_only, classical_sobel, alpha=0.08, color='blue')
    ax5b.set_xlabel('Image side length N', fontsize=12)
    ax5b.set_ylabel('Total operations', fontsize=12)
    ax5b.set_title(f'Three Regimes (k={k_example}, p={p_ex})', fontsize=13)
    ax5b.legend(fontsize=9, loc='upper left')
    ax5b.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

    # ------------------------------------------------------------------
    # Section 9: NISQ context
    # ------------------------------------------------------------------
    st.header("9. NISQ Era Context and Practical Implications")
    st.markdown(r"""
    **Current Status (NISQ Era):**

    | Factor | Status | Impact |
    |--------|--------|--------|
    | Gate speed | ~10-1000 ns/gate | $c_q' \gg c_{\text{cl}}$: classical faster in wall-clock |
    | Qubit count | ~100-1000 (noisy) | Limits patch size; BR makes small patches practical |
    | Error rates | ~$10^{-3}$--$10^{-2}$ | Requires error mitigation; limits circuit depth |
    | QRAM | Not yet available | Encoding bottleneck remains $O(p^2)$ |

    **Where QHED-BR shines today:**

    1. **Space efficiency**: Even with just **5-13 qubits**, arbitrarily large images can be processed.
       This is the most unambiguous quantum advantage -- exponential memory compression.

    2. **Polynomial BR overhead**: Boundary restoration adds only a factor of $(p/(p-2))^2$
       additional patches, which converges rapidly to 1.

    3. **NISQ-friendly circuits**: QHED circuits are shallow (depth $O(\log p)$ for detection),
       making them resilient to decoherence.

    **Future outlook:**

    - **Fault-tolerant quantum computers** ($c_q' \to c_{\text{cl}}$): End-to-end QHED matches classical.
    - **QRAM availability**: Encoding drops to $O(\log p^2)$, unlocking full detection-only speedup.
    - **Larger qubit counts**: Bigger patches ($p \geq 64$) yield $>$300x detection speedup.

    The fundamental insight of QHED-BR is that it provides a **practical, NISQ-compatible framework**
    for quantum image processing that offers immediate space advantages and positions itself to
    capture time advantages as quantum hardware improves.
    """)

    st.markdown("---")
    st.markdown("""
    **References:**
    - Shende, Bullock & Markov, "Synthesis of quantum logic circuits," IEEE Trans. CAD, 2006
    - Draper, "Addition on a quantum computer," arXiv:quant-ph/0008033, 2000
    - Cuccaro et al., "A new quantum ripple-carry addition circuit," arXiv:quant-ph/0410184, 2004
    - Yao et al., "Quantum image processing and its application to edge detection," Physical Review X 7.3, 2017
    - [Qiskit - Open-source quantum computing SDK](https://qiskit.org/)
    - [IBM Quantum Computing](https://quantum-computing.ibm.com/)
    """)
