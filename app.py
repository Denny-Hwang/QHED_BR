"""
QHED-BR: Quantum Hadamard Edge Detection with Boundary Restoration
Interactive Streamlit Application
"""

import io
import os
import sys
import time
import traceback

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Page config — MUST be the first Streamlit command
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="QHED-BR: Quantum Edge Detection",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Import project modules with error handling
# ---------------------------------------------------------------------------
try:
    from basicFunctions import load_image_from_array, amplitude_encode
    from qhed import QHED, build_qhed_circuit, edge_detection_stride
    from classical_ed_methods import (
        sobel_edge_detection,
        prewitt_edge_detection,
        laplacian_edge_detection,
        canny_edge_detection,
    )
except Exception as e:
    st.error(
        f"Failed to import required modules.\n\n"
        f"**Python {sys.version}**\n\n"
        f"```\n{traceback.format_exc()}\n```"
    )
    st.stop()

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
        "5. IBM Quantum Hardware",
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
            list(range(4, 9)),
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

    # Memory and patch count warnings
    est_patch_size = 2 ** patch_qb
    est_total_qb = 2 * patch_qb + 1
    est_stride = max(est_patch_size - 2, 1)
    est_patches = int(np.ceil((img_size - 2) / est_stride)) ** 2 if img_size > est_patch_size else 1

    if patch_qb >= 7:
        st.error(
            f"Patch size {est_patch_size}x{est_patch_size} ({est_total_qb} qubits): "
            f"statevector requires a 2^{est_total_qb} = {2**est_total_qb:,} dimensional vector. "
            f"The unitary matrix alone needs ~{(2**est_total_qb)**2 * 8 / 1e9:.1f} GB. "
            f"This will likely run out of memory."
        )
    elif patch_qb >= 6:
        st.warning(
            f"Patch size {est_patch_size}x{est_patch_size} ({est_total_qb} qubits): "
            f"statevector simulation operates on a 2^{est_total_qb} = {2**est_total_qb:,} "
            f"dimensional vector. This may be slow for large images."
        )

    if est_patches > 500:
        st.warning(
            f"~{est_patches} patches estimated with current settings. "
            f"This may take a long time and use significant memory. "
            f"Consider increasing patch qubits or reducing image size."
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
                progress_bar.progress(min(current / total, 1.0),
                                      text=f"Processing patch {current}/{total}...")

            try:
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
            except Exception as e:
                st.error(f"QHED execution failed: {e}")
                st.stop()

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

            try:
                progress1 = st.progress(0, text="Without restoration...")
                start1 = time.time()
                result_no_br, n1 = edge_detection_stride(
                    gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                    stride_mode='without_restoration',
                    progress_callback=lambda c, t: progress1.progress(min(c/t, 1.0), text=f"No BR: {c}/{t}")
                )
                time_no_br = time.time() - start1
                progress1.progress(1.0, text="Done (without restoration)")

                progress2 = st.progress(0, text="With restoration...")
                start2 = time.time()
                result_br, n2 = edge_detection_stride(
                    gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                    stride_mode='with_restoration',
                    progress_callback=lambda c, t: progress2.progress(min(c/t, 1.0), text=f"BR: {c}/{t}")
                )
                time_br = time.time() - start2
                progress2.progress(1.0, text="Done (with restoration)")
            except Exception as e:
                st.error(f"QHED execution failed: {e}")
                st.stop()

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
            try:
                progress = st.progress(0, text="Running QHED...")
                start = time.time()
                qhed_res, n_q = edge_detection_stride(
                    gray, width_qb=patch_qb, thr_ratio=thr_ratio,
                    stride_mode=stride_mode,
                    progress_callback=lambda c, t: progress.progress(min(c/t, 1.0), text=f"QHED: {c}/{t}")
                )
                all_results['QHED'] = qhed_res.astype(float)
                all_times['QHED'] = time.time() - start
                progress.progress(1.0, text="QHED done")
            except Exception as e:
                st.error(f"QHED execution failed: {e}")
                st.stop()

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
    st.title("Computational Complexity: QHED-BR vs Classical")

    # ------------------------------------------------------------------
    # Section 1: Notation
    # ------------------------------------------------------------------
    st.header("1. Notation and Definitions")
    st.markdown(
        "We compare QHED-BR against classical edge detection. "
        "All comparisons use **Boundary Restoration (BR)** since it is essential for correct results."
    )
    st.markdown("""
| Symbol | Definition |
|--------|-----------|
| $N$ | Image side length ($N \\times N$ image) |
| $p = 2^k$ | Patch side length ($p \\times p$ patch) |
| $k$ | Qubits per spatial dimension ($k \\geq 3$, minimum 8x8 patches) |
| $q = 2k + 1$ | Total qubits per QHED circuit ($2k$ data + 1 ancilla) |
| $Q$ | Number of patches with BR |
| $\\alpha$ | Hardware speed ratio = (time per quantum gate) / (time per classical op) |
""")
    st.markdown("**Patch count with BR** (stride $= p - 2$, 2-pixel overlap for boundary zeroing):")
    st.latex(r"Q_{\text{BR}} = \left\lceil \frac{N - 2}{p - 2} \right\rceil^2 \approx \frac{N^2}{(p-2)^2} \;\;\text{for}\; N \gg p")

    # ------------------------------------------------------------------
    # Section 2: Per-patch breakdown
    # ------------------------------------------------------------------
    st.header("2. QHED: Per-Patch Operation Breakdown")
    st.markdown(
        "Each QHED patch passes through three stages. "
        "The cost of each stage determines whether quantum processing beats classical."
    )

    st.subheader("Stage 1: Amplitude Encoding (Classical -> Quantum)")
    st.markdown(
        "The $p^2$ pixel values are encoded into quantum state amplitudes:"
    )
    st.latex(r"|\psi\rangle = \sum_{i=0}^{p^2 - 1} a_i |i\rangle, \quad \sum |a_i|^2 = 1")
    st.markdown(
        "Arbitrary state preparation on $m$ qubits requires $O(2^m)$ CNOT gates "
        "(Shende, Bullock & Markov, 2006). For $m = 2k$ data qubits, run twice for H/V scans:"
    )
    st.latex(r"G_{\text{encode}} = 2 \times O(2^{2k}) = 2p^2 \;\text{quantum gates per patch}")

    st.subheader("Stage 2: Quantum Edge Detection")
    st.markdown("The detection circuit: $H \\to D_{2n-1} \\to H$ on $q = 2k+1$ qubits.")
    st.markdown(
        "The permutation unitary $D_{2n-1}$ maps $|x\\rangle \\to |x + 1 \\bmod 2^q\\rangle$. "
        "This is a **quantum increment circuit**, decomposable into $O(q)$ Toffoli gates "
        "(Takahashi & Kunihiro, 2005). Using $c_D \\approx 10$ elementary gates per qubit "
        "as a practical estimate (accounting for Toffoli decomposition):"
    )
    st.latex(r"G_{\text{detect}} = 2 \times c_D \cdot q = 2 c_D (2k+1) \approx 40k \;\text{quantum gates per patch}")
    st.markdown(
        "**This is where quantum parallelism shines**: a single circuit of $O(k)$ gates "
        "computes all $p^2 = 2^{2k}$ pixel differences simultaneously. "
        "A classical method needs $O(p^2)$ operations for the same pixels."
    )

    st.subheader("Stage 3: Readout (Quantum -> Classical)")
    st.markdown(
        "Extract $p^2$ amplitudes from the statevector and threshold for edges. "
        "Two scan directions, each requiring extraction + threshold:"
    )
    st.latex(r"C_{\text{readout}} = 4p^2 \;\text{classical ops per patch}")

    st.markdown("---")
    st.markdown("**Summary per patch:**")
    st.markdown("""
| Stage | Count | Type |
|-------|-------|------|
| Encoding | $2p^2$ | Quantum gates |
| Detection | $\\sim 40k$ | Quantum gates |
| Readout | $4p^2$ | Classical ops |
| **Quantum total** | $\\mathbf{2p^2 + 40k}$ | **Quantum gates** |
| **Classical total** | $\\mathbf{4p^2}$ | **Classical ops** |
""")

    # ------------------------------------------------------------------
    # Section 3: Classical
    # ------------------------------------------------------------------
    st.header("3. Classical Edge Detection Complexity")
    st.markdown("""
| Method | Kernel | Ops/pixel | Total |
|--------|--------|-----------|-------|
| **Sobel** | Two $3 \\times 3$ kernels ($G_x, G_y$) | $\\sim 2 \\times 17 + 3 \\approx 37$ | $37 N^2$ |
| **Prewitt** | Two $3 \\times 3$ kernels | $\\sim 37$ | $37 N^2$ |
| **Laplacian** | One $3 \\times 3$ kernel | $\\sim 17$ | $17 N^2$ |
| **Canny** | Blur + gradient + NMS + hysteresis | $\\sim 100$ | $100 N^2$ |
""")
    st.markdown("All methods:")
    st.latex(r"T_{\text{classical}} = c_{\text{cl}} \cdot N^2 \;\;\text{classical operations}")
    st.markdown("where $c_{\\text{cl}} \\approx 37$ for Sobel and $c_{\\text{cl}} \\approx 100$ for Canny.")

    # ------------------------------------------------------------------
    # Section 4: Case 1
    # ------------------------------------------------------------------
    st.header("4. Case 1: Detection Only (Excluding Encoding/Decoding)")
    st.markdown(
        "If quantum data is **already loaded** (e.g., via QRAM or native quantum sensors), "
        "we isolate the pure quantum detection advantage."
    )

    st.markdown("**Total quantum detection gates for full image:**")
    st.latex(r"G_{\text{detect}}^{\text{total}} = Q_{\text{BR}} \times 40k = \frac{40k \cdot N^2}{(p-2)^2}")

    st.markdown("**Total execution time** with hardware speed ratio $\\alpha$:")
    st.latex(r"T_{\text{QHED}}^{(\text{det})} = \alpha \cdot \frac{40k \cdot N^2}{(p-2)^2}")
    st.latex(r"T_{\text{classical}} = c_{\text{cl}} \cdot N^2")

    st.markdown("**Quantum wins** when $T_{\\text{QHED}}^{(\\text{det})} < T_{\\text{classical}}$:")
    st.latex(r"\alpha < \frac{c_{\text{cl}} \cdot (p-2)^2}{40k} \;\; \stackrel{\text{def}}{=} \;\; \alpha_{\max}^{(\text{det})}")

    # Compute table values
    c_D_const = 10  # gates per qubit for D_{2n-1}
    det_gate_factor = 2 * 2 * c_D_const  # 2 directions × 2c_D per direction = 40

    st.markdown("**Crossover table (detection only):**")
    det_rows = []
    for k_val in [3, 4, 5, 6, 7]:
        p_val = 2 ** k_val
        alpha_sobel = 37 * (p_val - 2)**2 / (det_gate_factor * k_val)
        alpha_canny = 100 * (p_val - 2)**2 / (det_gate_factor * k_val)
        det_rows.append(
            f"| {k_val} | {p_val} | {37*(p_val-2)**2:,} | {det_gate_factor*k_val} | "
            f"**{alpha_sobel:.1f}** | **{alpha_canny:.1f}** |"
        )
    st.markdown(
        "| $k$ | $p$ | $c_{\\text{cl}}(p-2)^2$ (Sobel) | $40k$ | "
        "$\\alpha_{\\max}$ vs Sobel | $\\alpha_{\\max}$ vs Canny |\n"
        "|-----|-----|---:|---:|---:|---:|\n" + "\n".join(det_rows)
    )
    st.markdown(
        "Even with $\\alpha = 100$ (current NISQ estimate), quantum detection beats Canny for $k \\geq 4$ "
        "and beats Sobel for $k \\geq 5$. "
        "At $\\alpha = 10$ (near-term target), quantum beats Sobel for all $k \\geq 3$."
    )

    # --- Graph: Case 1 ---
    st.subheader("Case 1 Visualization")

    sizes = np.array([2**i for i in range(4, 12)])  # 16 to 2048

    fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Total ops vs N for alpha=1
    for k in [3, 4, 5, 6]:
        p = 2 ** k
        stride = max(p - 2, 1)
        Q_br = np.array([int(np.ceil((s - 2) / stride)) ** 2 if s >= p else 1 for s in sizes])
        ops = Q_br * det_gate_factor * k  # quantum gates (alpha=1)
        ax1a.plot(sizes, ops, 'o-', label=f'QHED k={k} (p={p})', linewidth=2, markersize=5)

    ax1a.plot(sizes, 37 * sizes**2, 'k^--', label='Sobel (37 ops/px)', linewidth=2.5, markersize=7)
    ax1a.plot(sizes, 100 * sizes**2, 'ks--', label='Canny (100 ops/px)', linewidth=2, markersize=5, alpha=0.6)
    ax1a.set_xlabel('Image side length N', fontsize=12)
    ax1a.set_ylabel('Total operations', fontsize=12)
    ax1a.set_title(r'Detection Only ($\alpha=1$)', fontsize=13)
    ax1a.set_yscale('log')
    ax1a.set_xscale('log', base=2)
    ax1a.legend(fontsize=8)
    ax1a.grid(True, alpha=0.3)

    # Right: Max alpha for quantum advantage vs k
    k_arr = np.arange(3, 9)
    p_arr = 2.0 ** k_arr
    alpha_max_sobel = 37 * (p_arr - 2)**2 / (det_gate_factor * k_arr)
    alpha_max_canny = 100 * (p_arr - 2)**2 / (det_gate_factor * k_arr)
    x_pos = np.arange(len(k_arr))
    width = 0.35
    ax1b.bar(x_pos - width/2, alpha_max_sobel, width, label='vs Sobel', color='#2196F3', edgecolor='black', linewidth=0.5)
    ax1b.bar(x_pos + width/2, alpha_max_canny, width, label='vs Canny', color='#FF9800', edgecolor='black', linewidth=0.5)
    ax1b.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label=r'Current NISQ $\alpha \approx 100$')
    ax1b.axhline(y=10, color='green', linestyle=':', linewidth=1.5, label=r'Near-term $\alpha \approx 10$')
    for i, (as_, ac_) in enumerate(zip(alpha_max_sobel, alpha_max_canny)):
        ax1b.text(i - width/2, as_ * 1.1, f'{as_:.0f}', ha='center', fontsize=8, fontweight='bold')
        ax1b.text(i + width/2, ac_ * 1.1, f'{ac_:.0f}', ha='center', fontsize=8, fontweight='bold')
    ax1b.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax1b.set_ylabel(r'Max $\alpha$ for quantum advantage', fontsize=12)
    ax1b.set_title('Detection-Only: Crossover Threshold', fontsize=13)
    ax1b.set_xticks(x_pos)
    ax1b.set_xticklabels([f'k={k}\np={2**k}' for k in k_arr], fontsize=9)
    ax1b.set_yscale('log')
    ax1b.legend(fontsize=8)
    ax1b.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    # ------------------------------------------------------------------
    # Section 5: Case 2
    # ------------------------------------------------------------------
    st.header("5. Case 2: End-to-End (Including Encoding & Decoding)")
    st.markdown(
        "In practice, classical image data must be encoded into quantum states "
        "and results read out. This is the honest comparison for current systems."
    )

    st.markdown("**Total execution time** (quantum + classical readout):")
    st.latex(r"T_{\text{QHED}}^{(\text{e2e})} = \underbrace{\alpha \cdot Q_{\text{BR}} \cdot (2p^2 + 40k)}_{\text{quantum gates}} \;+\; \underbrace{Q_{\text{BR}} \cdot 4p^2}_{\text{classical readout}}")

    st.markdown("**Quantum wins** when $T_{\\text{QHED}}^{(\\text{e2e})} < T_{\\text{classical}} = c_{\\text{cl}} N^2$:")
    st.latex(r"\alpha \cdot \frac{2p^2 + 40k}{(p-2)^2} + \frac{4p^2}{(p-2)^2} < c_{\text{cl}}")

    st.markdown("Solving for the maximum tolerable hardware speed ratio:")
    st.latex(r"\alpha_{\max}^{(\text{e2e})} = \frac{c_{\text{cl}}(p-2)^2 - 4p^2}{2p^2 + 40k}")

    st.markdown("**Crossover table (end-to-end):**")
    e2e_rows = []
    for k_val in [3, 4, 5, 6, 7]:
        p_val = 2 ** k_val
        readout_term = 4 * p_val**2 / (p_val - 2)**2
        alpha_sobel = (37 * (p_val-2)**2 - 4 * p_val**2) / (2 * p_val**2 + det_gate_factor * k_val)
        alpha_canny = (100 * (p_val-2)**2 - 4 * p_val**2) / (2 * p_val**2 + det_gate_factor * k_val)
        e2e_rows.append(
            f"| {k_val} | {p_val} | {readout_term:.2f} | "
            f"**{alpha_sobel:.1f}** | **{alpha_canny:.1f}** |"
        )
    st.markdown(
        "| $k$ | $p$ | Readout overhead $4p^2/(p-2)^2$ | "
        "$\\alpha_{\\max}$ vs Sobel | $\\alpha_{\\max}$ vs Canny |\n"
        "|-----|-----|---:|---:|---:|\n" + "\n".join(e2e_rows)
    )

    st.markdown("""
**Key insight:** With encoding included, both QHED-BR and classical are $O(N^2)$.
The crossover depends entirely on the hardware constant $\\alpha$:

- **Current NISQ** ($\\alpha \\approx 100$--$10{,}000$): Classical wins for all $k$.
  Encoding $2p^2$ quantum gates per patch dominates, and each gate is slow.
- **Near-term** ($\\alpha \\approx 10$): Quantum competitive vs Canny for $k \\geq 4$.
- **Fault-tolerant** ($\\alpha \\approx 1$): Quantum wins for all $k \\geq 3$.
- **With QRAM** ($O(\\log p^2)$ encoding): Eliminates the encoding bottleneck,
  recovering Case 1's advantage even end-to-end.
""")

    # --- Graph: Case 2 ---
    st.subheader("Case 2 Visualization")

    fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: Total ops vs N at alpha=1
    for k in [3, 4, 5, 6]:
        p = 2 ** k
        stride = max(p - 2, 1)
        Q_br = np.array([int(np.ceil((s - 2) / stride)) ** 2 if s >= p else 1 for s in sizes])
        # alpha=1: quantum gates = classical ops
        ops = Q_br * (2 * p**2 + det_gate_factor * k) + Q_br * 4 * p**2  # quantum + readout
        ax2a.plot(sizes, ops, 'o-', label=f'QHED k={k} (p={p})', linewidth=2, markersize=5)

    ax2a.plot(sizes, 37 * sizes**2, 'k^--', label='Sobel (37 ops/px)', linewidth=2.5, markersize=7)
    ax2a.plot(sizes, 100 * sizes**2, 'ks--', label='Canny (100 ops/px)', linewidth=2, markersize=5, alpha=0.6)
    ax2a.set_xlabel('Image side length N', fontsize=12)
    ax2a.set_ylabel('Total operations', fontsize=12)
    ax2a.set_title(r'End-to-End ($\alpha=1$, optimistic)', fontsize=13)
    ax2a.set_yscale('log')
    ax2a.set_xscale('log', base=2)
    ax2a.legend(fontsize=8)
    ax2a.grid(True, alpha=0.3)

    # Right: Max alpha for e2e advantage vs k (grouped bar)
    alpha_e2e_sobel = np.array([
        (37 * (2**k - 2)**2 - 4 * 4**k) / (2 * 4**k + det_gate_factor * k)
        for k in k_arr
    ])
    alpha_e2e_canny = np.array([
        (100 * (2**k - 2)**2 - 4 * 4**k) / (2 * 4**k + det_gate_factor * k)
        for k in k_arr
    ])
    ax2b.bar(x_pos - width/2, alpha_e2e_sobel, width, label='vs Sobel', color='#2196F3', edgecolor='black', linewidth=0.5)
    ax2b.bar(x_pos + width/2, alpha_e2e_canny, width, label='vs Canny', color='#FF9800', edgecolor='black', linewidth=0.5)
    ax2b.axhline(y=10, color='green', linestyle=':', linewidth=1.5, label=r'Near-term $\alpha \approx 10$')
    ax2b.axhline(y=1, color='red', linestyle='--', linewidth=1.5, label=r'Fault-tolerant $\alpha \approx 1$')
    for i, (as_, ac_) in enumerate(zip(alpha_e2e_sobel, alpha_e2e_canny)):
        ax2b.text(i - width/2, as_ + 0.3, f'{as_:.1f}', ha='center', fontsize=8, fontweight='bold')
        ax2b.text(i + width/2, ac_ + 0.3, f'{ac_:.1f}', ha='center', fontsize=8, fontweight='bold')
    ax2b.set_xlabel('k (qubits per dimension)', fontsize=12)
    ax2b.set_ylabel(r'Max $\alpha$ for quantum advantage', fontsize=12)
    ax2b.set_title('End-to-End: Crossover Threshold', fontsize=13)
    ax2b.set_xticks(x_pos)
    ax2b.set_xticklabels([f'k={k}\np={2**k}' for k in k_arr], fontsize=9)
    ax2b.legend(fontsize=8)
    ax2b.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # ------------------------------------------------------------------
    # Section 6: Space complexity
    # ------------------------------------------------------------------
    st.header("6. Space Complexity: Exponential Memory Advantage")
    st.markdown(
        "Regardless of time overhead, QHED achieves an **exponential advantage in space**. "
        "This is the most unambiguous quantum advantage:"
    )
    st.latex(r"\text{Classical: } O(p^2) = O(2^{2k}) \text{ memory cells per patch}")
    st.latex(r"\text{Quantum: } O(q) = O(2k+1) \text{ qubits per patch}")
    st.latex(r"\text{Compression ratio} = \frac{2^{2k}}{2k+1} \;\xrightarrow{k \to \infty}\; \text{exponential}")

    st.markdown("""
| Patch | Pixels | Classical | Quantum | Compression |
|-------|--------|-----------|---------|-------------|
| $8 \\times 8$ | 64 | 64 values | **7** qubits | 9.1x |
| $16 \\times 16$ | 256 | 256 values | **9** qubits | 28.4x |
| $32 \\times 32$ | 1024 | 1024 values | **11** qubits | 93.1x |
| $64 \\times 64$ | 4096 | 4096 values | **13** qubits | 315.1x |
| $128 \\times 128$ | 16384 | 16384 values | **15** qubits | 1092.3x |
| $256 \\times 256$ | 65536 | 65536 values | **17** qubits | 3855.1x |
""")

    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 5.5))

    k_vals = np.arange(3, 10)
    p_vals = 2 ** k_vals
    classical_mem = p_vals ** 2
    quantum_mem = 2 * k_vals + 1
    compression = classical_mem / quantum_mem

    ax3a.semilogy(k_vals, classical_mem, 'ro-', label=r'Classical: $p^2 = 2^{2k}$', linewidth=2.5, markersize=8)
    ax3a.semilogy(k_vals, quantum_mem, 'bs-', label=r'Quantum: $2k+1$', linewidth=2.5, markersize=8)
    ax3a.fill_between(k_vals, quantum_mem, classical_mem, alpha=0.15, color='green', label='Exponential gap')
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
    ax3b.set_ylabel(r'Compression ratio ($p^2 / (2k+1)$)', fontsize=12)
    ax3b.set_title('Memory Compression Ratio', fontsize=13)
    ax3b.set_yscale('log')
    ax3b.grid(True, alpha=0.3, axis='y')
    ax3b.set_xticks(k_vals)
    ax3b.set_xticklabels([f'k={k}\np={2**k}' for k in k_vals], fontsize=8)

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    # ------------------------------------------------------------------
    # Section 7: Patch count
    # ------------------------------------------------------------------
    st.header("7. BR Overhead: Patch Count Analysis")
    st.markdown("BR increases patch count by a polynomial factor that vanishes for large $p$:")
    st.latex(r"\frac{Q_{\text{BR}}}{Q_{\text{no-BR}}} = \left(\frac{p}{p-2}\right)^2 \;\xrightarrow{p \to \infty}\; 1")

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
        k_overhead = np.arange(3, 9)
        p_overhead = 2.0 ** k_overhead
        overhead_ratio = (p_overhead / (p_overhead - 2)) ** 2
        colors_oh = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4']
        ax4b.bar(k_overhead, overhead_ratio, color=colors_oh, edgecolor='black', linewidth=0.5)
        ax4b.axhline(y=1.0, color='gray', linestyle='--', linewidth=1.5, label='No overhead (1.0x)')
        for ki, oh in zip(k_overhead, overhead_ratio):
            ax4b.text(ki, oh + 0.02, f'{oh:.2f}x', ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax4b.set_xlabel('k (qubits per dimension)', fontsize=12)
        ax4b.set_ylabel(r'Patch overhead ratio $(p/(p-2))^2$', fontsize=12)
        ax4b.set_title('BR Overhead (converges to 1.0)', fontsize=13)
        ax4b.set_xticks(k_overhead)
        ax4b.set_xticklabels([f'k={k}\np={2**k}' for k in k_overhead], fontsize=9)
        ax4b.legend(fontsize=10)
        ax4b.grid(True, alpha=0.3, axis='y')
        ax4b.set_ylim(0.9, max(overhead_ratio) + 0.15)
        st.pyplot(fig4b)
        plt.close(fig4b)

    # ------------------------------------------------------------------
    # Section 8: Combined crossover
    # ------------------------------------------------------------------
    st.header("8. Combined Crossover: Three Regimes")
    st.markdown(
        "The following plot shows all three operation regimes for a representative case ($k=4$, $p=16$):"
    )

    fig5, ax5 = plt.subplots(figsize=(12, 6))

    N_range = np.logspace(np.log10(16), np.log10(4096), 200)
    k_ex, p_ex = 4, 16
    stride_ex = p_ex - 2
    Q_ex = np.ceil((N_range - 2) / stride_ex) ** 2

    detect_ops = Q_ex * det_gate_factor * k_ex
    e2e_alpha1 = Q_ex * (2 * p_ex**2 + det_gate_factor * k_ex) + Q_ex * 4 * p_ex**2
    e2e_alpha10 = 10 * Q_ex * (2 * p_ex**2 + det_gate_factor * k_ex) + Q_ex * 4 * p_ex**2
    e2e_alpha100 = 100 * Q_ex * (2 * p_ex**2 + det_gate_factor * k_ex) + Q_ex * 4 * p_ex**2
    sobel_ops = 37 * N_range ** 2
    canny_ops = 100 * N_range ** 2

    ax5.loglog(N_range, sobel_ops, 'k-', label='Sobel (37 ops/px)', linewidth=2.5)
    ax5.loglog(N_range, canny_ops, 'k--', label='Canny (100 ops/px)', linewidth=2, alpha=0.7)
    ax5.loglog(N_range, detect_ops, 'b-', label=r'QHED detect only ($\alpha$=1)', linewidth=2)
    ax5.loglog(N_range, e2e_alpha1, 'g-', label=r'QHED e2e $\alpha$=1 (fault-tol.)', linewidth=2)
    ax5.loglog(N_range, e2e_alpha10, 'r--', label=r'QHED e2e $\alpha$=10 (near-term)', linewidth=2)
    ax5.loglog(N_range, e2e_alpha100, 'r:', label=r'QHED e2e $\alpha$=100 (NISQ)', linewidth=2, alpha=0.7)

    ax5.fill_between(N_range, detect_ops, sobel_ops, alpha=0.06, color='blue')
    ax5.annotate(r'Quantum advantage zone (detection only)', xy=(200, 3e4), fontsize=10, color='blue', alpha=0.8)

    ax5.set_xlabel('Image side length N', fontsize=13)
    ax5.set_ylabel('Total equivalent operations', fontsize=13)
    ax5.set_title(f'Three Regimes: QHED-BR (k={k_ex}, p={p_ex}) vs Classical', fontsize=14)
    ax5.legend(fontsize=9, loc='upper left')
    ax5.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

    # ------------------------------------------------------------------
    # Section 9: Summary
    # ------------------------------------------------------------------
    st.header("9. Summary and Conclusions")

    st.markdown("**Advantage comparison:**")
    st.markdown("""
| Dimension | Classical | QHED-BR | Winner |
|-----------|----------|---------|--------|
| **Time (detection only)** | $c_{\\text{cl}} \\cdot N^2$ | $\\frac{40k \\cdot N^2}{(p-2)^2}$ | Quantum: speedup $\\propto p^2/k$ |
| **Time (end-to-end)** | $c_{\\text{cl}} \\cdot N^2$ | $\\sim \\frac{6p^2 \\cdot N^2}{(p-2)^2}$ | **Same** $O(N^2)$: depends on $\\alpha$ |
| **Space** | $O(p^2)$ per patch | $O(k)$ qubits | Quantum: **exponential** |
| **BR overhead** | -- | $(p/(p-2))^2 \\to 1$ | Polynomial, vanishes |
""")

    st.markdown("**Honest assessment:**")
    st.markdown("""
1. **Detection only**: QHED has a genuine, provable advantage of
   $\\Theta(p^2/k)$ fewer operations. This is significant -- at $k=5$ ($p=32$),
   the speedup exceeds 100x even accounting for hardware penalty.

2. **End-to-end**: The $O(p^2)$ encoding cost neutralizes the detection advantage.
   Both methods are $O(N^2)$, and the winner depends on hardware speed $\\alpha$.
   - $\\alpha < 4$: quantum wins vs Sobel for $k \\geq 3$
   - $\\alpha < 10$: quantum wins vs Canny for $k \\geq 3$
   - $\\alpha > 15$: classical wins for all $k$ vs Sobel

3. **Space**: The exponential compression ($2^{2k} \\to 2k+1$) is hardware-independent
   and represents the clearest quantum advantage of QHED-BR.

4. **NISQ reality**: Current quantum gates are ~$100$--$10{,}000\\times$ slower than
   classical FLOPs. End-to-end, classical methods are currently faster.
   However, QHED-BR circuits are **shallow** ($O(k)$ depth), making them
   among the most NISQ-friendly quantum algorithms.
""")

    st.markdown("---")
    st.markdown("""
**References:**
- Shende, Bullock & Markov, "Synthesis of quantum logic circuits," IEEE Trans. CAD, 2006
- Takahashi & Kunihiro, "A linear-size quantum circuit for addition with no ancillary qubits," Quantum Inf. Comput. 5(6), 2005
- Cuccaro et al., "A new quantum ripple-carry addition circuit," arXiv:quant-ph/0410184, 2004
- Yao et al., "Quantum image processing and its application to edge detection," Physical Review X 7.3, 2017
- [Qiskit](https://qiskit.org/) | [IBM Quantum](https://quantum-computing.ibm.com/)
""")


# ===================================================================
# PAGE 5: IBM Quantum Hardware
# ===================================================================
elif page == "5. IBM Quantum Hardware":
    st.title("Run QHED on Real IBM Quantum Hardware")

    st.warning(
        "Your API keys are used **only for this session** and are **never stored** "
        "on disk, logged, or transmitted anywhere other than IBM's servers. "
        "They exist only in your browser's session memory and are discarded when you close the tab."
    )

    # --- Authentication ---
    st.header("1. IBM Quantum Authentication")
    st.markdown("""
Two connection channels are supported. Fill in **one** set of credentials:
- **IBM Cloud**: Use an IBM Cloud API Key + Cloud Resource Name (CRN) instance.
- **IBM Quantum Platform**: Use an IBM Quantum API token (from [quantum.ibm.com](https://quantum.ibm.com/)).
""")

    col_auth1, col_auth2 = st.columns(2)
    with col_auth1:
        st.subheader("Option A: IBM Cloud")
        cloud_api_key = st.text_input("IBM Cloud API Key", type="password", key="cloud_key")
        cloud_instance = st.text_input(
            "CRN Instance",
            placeholder="crn:v1:bluemix:public:quantum-computing:...",
            key="cloud_instance",
        )
    with col_auth2:
        st.subheader("Option B: IBM Quantum Platform")
        quantum_token = st.text_input("IBM Quantum API Token", type="password", key="quantum_token")
        st.markdown(
            "Get your token at [quantum.ibm.com](https://quantum.ibm.com/) > "
            "Account Settings > API Token."
        )

    # Preferred backends (Heron r2 first)
    PREFERRED_BACKENDS = ['ibm_marrakesh', 'ibm_fez', 'ibm_torino', 'ibm_kyiv', 'ibm_sherbrooke']

    # --- Connect ---
    if 'ibm_service' not in st.session_state:
        st.session_state['ibm_service'] = None
        st.session_state['ibm_backend'] = None
        st.session_state['ibm_backend_name'] = None
        st.session_state['ibm_hw_result'] = None

    if st.button("Connect to IBM Quantum", type="primary"):
        st.session_state['ibm_service'] = None
        st.session_state['ibm_backend'] = None
        st.session_state['ibm_backend_name'] = None

        connection_attempts = []

        # Build attempt list based on what the user filled in
        if cloud_api_key and cloud_instance:
            connection_attempts.append(
                ("ibm_cloud", {"channel": "ibm_cloud", "token": cloud_api_key, "instance": cloud_instance})
            )
        if quantum_token:
            connection_attempts.append(
                ("ibm_quantum", {"channel": "ibm_quantum", "token": quantum_token})
            )

        if not connection_attempts:
            st.error("Please enter at least one set of credentials.")
        else:
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService
            except ImportError:
                st.error(
                    "qiskit-ibm-runtime is not installed. "
                    "Run: `pip install qiskit-ibm-runtime`"
                )
                st.stop()

            connected = False
            for method, kwargs in connection_attempts:
                try:
                    service = QiskitRuntimeService(**kwargs)
                    st.session_state['ibm_service'] = service
                    st.success(f"Connected via **{method}**")
                    connected = True
                    break
                except Exception as e:
                    st.warning(f"{method}: {e}")

            if not connected:
                st.error("Failed to connect with the provided credentials.")
            else:
                # Select backend
                svc = st.session_state['ibm_service']
                backend_found = False
                for name in PREFERRED_BACKENDS:
                    try:
                        be = svc.backend(name)
                        status = be.status()
                        if status.operational:
                            st.session_state['ibm_backend'] = be
                            st.session_state['ibm_backend_name'] = name
                            st.success(
                                f"Backend: **{name}** ({be.num_qubits}Q, "
                                f"pending jobs: {status.pending_jobs})"
                            )
                            backend_found = True
                            break
                    except Exception:
                        continue

                if not backend_found:
                    # Fallback: least-busy backend
                    try:
                        be = svc.least_busy(operational=True, min_num_qubits=5)
                        st.session_state['ibm_backend'] = be
                        st.session_state['ibm_backend_name'] = be.name
                        status = be.status()
                        st.info(
                            f"No preferred backend available. Using least-busy: "
                            f"**{be.name}** ({be.num_qubits}Q, pending: {status.pending_jobs})"
                        )
                    except Exception as e:
                        st.error(f"No operational backend found: {e}")

    # Show connection status
    if st.session_state.get('ibm_backend_name'):
        st.info(f"Currently connected to: **{st.session_state['ibm_backend_name']}**")

    st.markdown("---")

    # --- Run on Hardware ---
    st.header("2. Run QHED on Real Hardware")
    st.markdown("""
Upload a small image and run QHED edge detection on actual IBM quantum hardware.
**Note:** Real hardware execution is much slower than simulation. A single patch may take
30 seconds to several minutes depending on queue times.
""")

    if st.session_state.get('ibm_backend') is None:
        st.info("Connect to IBM Quantum first (above) to enable hardware execution.")
        st.stop()

    # Image input
    hw_image_source = st.radio("Image source", ["Sample images", "Upload"], horizontal=True, key="hw_img_src")
    hw_input_image = None

    if hw_image_source == "Sample images":
        import os
        img_dir = os.path.join(os.path.dirname(__file__), 'images')
        img_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
        available = []
        for root, _dirs, files in os.walk(img_dir):
            for f in sorted(files):
                if f.lower().endswith(img_extensions):
                    rel = os.path.relpath(os.path.join(root, f), img_dir)
                    available.append(rel)
        available.sort()
        if available:
            hw_sel = st.selectbox("Select sample image", available, key="hw_img_sel")
            hw_input_image = np.array(Image.open(os.path.join(img_dir, hw_sel)))
        else:
            st.warning("No sample images found in ./images/")
    else:
        hw_uploaded = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg', 'bmp'], key="hw_upload")
        if hw_uploaded:
            hw_input_image = np.array(Image.open(hw_uploaded))

    if hw_input_image is None:
        st.info("Select or upload an image.")
        st.stop()

    st.image(hw_input_image, caption="Input image", width=250)

    # Parameters
    col_hw1, col_hw2, col_hw3 = st.columns(3)
    with col_hw1:
        hw_size_exp = st.selectbox("Resize to", [4, 5, 6], index=0,
                                    format_func=lambda x: f"{2**x}x{2**x}",
                                    key="hw_size")
        hw_size = 2 ** hw_size_exp
    with col_hw2:
        hw_patch_qb = st.selectbox("Patch qubits/dim", [3, 4], index=0,
                                    format_func=lambda x: f"k={x} ({2**x}x{2**x} patch, {2*x+1} qubits)",
                                    key="hw_patch")
    with col_hw3:
        hw_shots = st.selectbox("Shots", [1024, 4096, 8192], index=1, key="hw_shots")

    hw_patch_size = 2 ** hw_patch_qb
    hw_total_qb = 2 * hw_patch_qb + 1

    if hw_patch_size > hw_size:
        st.error(f"Patch size {hw_patch_size}x{hw_patch_size} exceeds image size {hw_size}x{hw_size}. Reduce patch qubits or increase image size.")
        st.stop()

    # Estimate patch count
    hw_stride = max(hw_patch_size - 2, 1)
    hw_est_patches = int(np.ceil((hw_size - 2) / hw_stride)) ** 2

    st.markdown(
        f"**Estimated:** {hw_est_patches} patches, {hw_total_qb} qubits/patch, "
        f"{hw_shots} shots/circuit on **{st.session_state['ibm_backend_name']}**"
    )

    if hw_est_patches > 25:
        st.warning(
            f"{hw_est_patches} patches will submit many jobs. "
            f"Consider reducing image size or increasing patch size."
        )

    if st.button("Run on IBM Quantum Hardware", type="primary", key="hw_run"):
        try:
            from qiskit_ibm_runtime import SamplerV2 as Sampler
            from qiskit import transpile as qk_transpile
            from qiskit import QuantumCircuit
        except ImportError:
            st.error("qiskit-ibm-runtime is required. Install with: pip install qiskit-ibm-runtime")
            st.stop()

        gray = load_image_from_array(hw_input_image, resize=(hw_size, hw_size))
        backend = st.session_state['ibm_backend']

        progress = st.progress(0, text="Preparing patches...")

        width_patch = hw_patch_size
        stride = hw_stride
        h, w = gray.shape

        row_pos = list(range(0, h - width_patch + 1, stride))
        if row_pos[-1] + width_patch < h:
            row_pos.append(h - width_patch)
        col_pos = list(range(0, w - width_patch + 1, stride))
        if col_pos[-1] + width_patch < w:
            col_pos.append(w - width_patch)

        result_img = np.zeros((h, w), dtype=np.float64)
        count_img = np.zeros((h, w), dtype=np.float64)
        interior_mask = np.ones((width_patch, width_patch), dtype=np.float64)
        interior_mask[0, :] = 0
        interior_mask[-1, :] = 0
        interior_mask[:, 0] = 0
        interior_mask[:, -1] = 0

        total_patches = len(row_pos) * len(col_pos)
        total_pixels = width_patch * width_patch
        data_qb = int(np.ceil(np.log2(total_pixels)))
        total_qb = data_qb + 1
        target_len = 2 ** data_qb

        sampler = Sampler(mode=backend)
        current = 0
        start_time = time.time()

        for r in row_pos:
            for c in col_pos:
                patch = gray[r:r + width_patch, c:c + width_patch]

                # Process H and V scans
                edge_results = {}
                for label, img_data in [('h', patch), ('v', patch.T)]:
                    norm = amplitude_encode(img_data)
                    if norm is None:
                        edge_results[label] = np.zeros(total_pixels)
                        continue

                    if len(norm) < target_len:
                        norm = np.pad(norm, (0, target_len - len(norm)))

                    D2n_1 = np.roll(np.identity(2 ** total_qb), 1, axis=1)

                    qc = QuantumCircuit(total_qb)
                    qc.initialize(norm.tolist(), range(1, total_qb))
                    qc.h(0)
                    qc.unitary(D2n_1, range(total_qb), label='D')
                    qc.h(0)
                    qc.measure_all()

                    qc_t = qk_transpile(qc, backend=backend, optimization_level=2)

                    try:
                        job = sampler.run([qc_t], shots=hw_shots)
                        result = job.result()
                        # Extract counts from SamplerV2
                        pub_result = result[0]
                        counts = pub_result.data.meas.get_counts()
                    except Exception as e:
                        st.warning(f"Patch ({r},{c}) {label}: {e}")
                        edge_results[label] = np.zeros(total_pixels)
                        continue

                    edge = np.zeros(total_pixels)
                    for i in range(total_pixels):
                        key = format(2 * i + 1, f'0{total_qb}b')
                        edge[i] = counts.get(key, 0)
                    edge_results[label] = edge

                # Combine H/V
                row_dim, col_dim = patch.shape
                edge_h = edge_results['h'][:row_dim * col_dim].reshape(row_dim, col_dim)
                edge_v = edge_results['v'][:col_dim * row_dim].reshape(col_dim, row_dim).T
                combined = edge_h + edge_v

                # Threshold
                mean_val = np.mean(combined[combined > 0]) if np.any(combined > 0) else 0
                thr = mean_val * 0.5
                edge_binary = (combined > thr).astype(np.float64)

                # Boundary zero
                from basicFunctions import boundary_zero as bz
                edge_binary = bz(edge_binary)

                result_img[r:r + width_patch, c:c + width_patch] += edge_binary
                count_img[r:r + width_patch, c:c + width_patch] += interior_mask

                current += 1
                elapsed = time.time() - start_time
                eta = (elapsed / current) * (total_patches - current) if current > 0 else 0
                progress.progress(
                    current / total_patches,
                    text=f"Patch {current}/{total_patches} | Elapsed: {elapsed:.0f}s | ETA: {eta:.0f}s"
                )

        count_img[count_img == 0] = 1
        hw_result = (result_img / count_img >= 0.5).astype(np.uint8)
        total_time = time.time() - start_time

        progress.progress(1.0, text=f"Done! Total: {total_time:.1f}s")

        st.session_state['ibm_hw_result'] = hw_result
        st.session_state['ibm_hw_gray'] = gray
        st.session_state['ibm_hw_time'] = total_time
        st.session_state['ibm_hw_patches'] = total_patches

    # Display results
    if st.session_state.get('ibm_hw_result') is not None:
        st.header("3. Results")
        hw_res = st.session_state['ibm_hw_result']
        hw_gray = st.session_state['ibm_hw_gray']
        hw_time = st.session_state['ibm_hw_time']
        hw_np = st.session_state['ibm_hw_patches']

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Original**")
            st.image(hw_gray, clamp=True, width=350)
        with col_r2:
            st.markdown(
                f"**QHED on {st.session_state['ibm_backend_name']}** "
                f"({hw_np} patches, {hw_time:.1f}s)"
            )
            st.image(hw_res.astype(float), clamp=True, width=350)

        # Compare with simulation
        if st.button("Compare with Simulation", key="hw_compare"):
            sim_progress = st.progress(0, text="Running simulation...")
            sim_start = time.time()
            sim_result, sim_n = edge_detection_stride(
                hw_gray,
                width_qb=st.session_state.get('hw_patch', 3),
                thr_ratio=0.7,
                stride_mode='with_restoration',
                patch_boundary_zero=True,
                progress_callback=lambda c, t: sim_progress.progress(c/t, text=f"Sim: {c}/{t}"),
            )
            sim_time = time.time() - sim_start
            sim_progress.progress(1.0, text="Done!")

            fig_cmp, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(hw_gray, cmap='gray')
            axes[0].set_title('Original')
            axes[0].axis('off')
            axes[1].imshow(sim_result, cmap='gray')
            axes[1].set_title(f'Simulation ({sim_n} patches, {sim_time:.2f}s)')
            axes[1].axis('off')
            axes[2].imshow(hw_res, cmap='gray')
            axes[2].set_title(
                f'IBM Hardware ({hw_np} patches, {hw_time:.1f}s)\n'
                f'{st.session_state["ibm_backend_name"]}'
            )
            axes[2].axis('off')
            plt.tight_layout()
            st.pyplot(fig_cmp)

            st.download_button(
                "Download comparison",
                fig_to_bytes(fig_cmp, dpi=200),
                file_name="qhed_hw_vs_sim.png",
                mime="image/png",
            )
            plt.close(fig_cmp)

        # Download
        st.download_button(
            "Download hardware result",
            img_to_bytes(hw_res),
            file_name=f"qhed_{st.session_state['ibm_backend_name']}.png",
            mime="image/png",
            key="hw_download",
        )
