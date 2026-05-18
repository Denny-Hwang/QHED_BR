"""Page 5 — IBM Quantum Hardware (with optional Demo Mode)."""

from __future__ import annotations

import os
import time

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from PIL import Image

from basicFunctions import amplitude_encode, boundary_zero, load_image_from_array
from qhed import D2n_1_circuit, edge_detection_stride
from ui.helpers import fig_to_bytes, img_to_bytes
from ui.i18n import t

PREFERRED_BACKENDS = ["ibm_marrakesh", "ibm_fez", "ibm_torino", "ibm_kyiv", "ibm_sherbrooke"]


def _select_image() -> np.ndarray | None:
    src = st.radio("Image source", ["Sample images", "Upload"], horizontal=True, key="hw_img_src")
    if src == "Sample images":
        img_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
        exts = (".png", ".jpg", ".jpeg", ".bmp")
        available = []
        for root, _dirs, files in os.walk(img_dir):
            for f in sorted(files):
                if f.lower().endswith(exts):
                    available.append(os.path.relpath(os.path.join(root, f), img_dir))
        available.sort()
        if not available:
            st.warning("No sample images found in ./images/")
            return None
        sel = st.selectbox("Select sample image", available, key="hw_img_sel")
        return np.array(Image.open(os.path.join(img_dir, sel)))
    uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "bmp"], key="hw_upload")
    if uploaded:
        return np.array(Image.open(uploaded))
    return None


def render() -> None:
    st.title("Run QHED on Real IBM Quantum Hardware")

    # Demo mode toggle lets visitors browse the page without entering credentials.
    demo_mode = st.toggle(
        t("ibm.demo_mode_toggle"),
        value=st.session_state.get("ibm_demo_mode", False),
        help=t("ibm.demo_mode_help"),
        key="ibm_demo_mode_toggle",
    )
    st.session_state["ibm_demo_mode"] = demo_mode

    if demo_mode:
        st.info(
            "Demo mode is **on**: no IBM credentials required. The page below "
            "describes what would happen on real hardware. Toggle off and provide "
            "credentials to actually run circuits."
        )

    st.warning(
        "Your API keys are used **only for this session** and are **never stored** "
        "on disk, logged, or transmitted anywhere other than IBM's servers. "
        "They exist only in your browser's session memory and are discarded when you close the tab."
    )

    st.header("1. IBM Quantum Authentication")
    st.markdown("""
Two connection channels are supported. Fill in **one** set of credentials:
- **IBM Cloud**: Use an IBM Cloud API Key + Cloud Resource Name (CRN) instance.
- **IBM Quantum Platform**: Use an IBM Quantum API token (from [quantum.ibm.com](https://quantum.ibm.com/)).
""")

    col_auth1, col_auth2 = st.columns(2)
    with col_auth1:
        st.subheader("Option A: IBM Cloud")
        cloud_api_key = st.text_input("IBM Cloud API Key", type="password", key="cloud_key",
                                      disabled=demo_mode)
        cloud_instance = st.text_input(
            "CRN Instance",
            placeholder="crn:v1:bluemix:public:quantum-computing:...",
            key="cloud_instance", disabled=demo_mode,
        )
    with col_auth2:
        st.subheader("Option B: IBM Quantum Platform")
        quantum_token = st.text_input("IBM Quantum API Token", type="password",
                                      key="quantum_token", disabled=demo_mode)
        st.markdown("Get your token at [quantum.ibm.com](https://quantum.ibm.com/) > Account Settings > API Token.")

    for k in ("ibm_service", "ibm_backend", "ibm_backend_name", "ibm_hw_result"):
        st.session_state.setdefault(k, None)

    if st.button("Connect to IBM Quantum", type="primary", disabled=demo_mode):
        st.session_state["ibm_service"] = None
        st.session_state["ibm_backend"] = None
        st.session_state["ibm_backend_name"] = None

        connection_attempts = []
        if cloud_api_key and cloud_instance:
            connection_attempts.append(("ibm_cloud", {"channel": "ibm_cloud", "token": cloud_api_key, "instance": cloud_instance}))
        if quantum_token:
            connection_attempts.append(("ibm_quantum", {"channel": "ibm_quantum", "token": quantum_token}))

        if not connection_attempts:
            st.error("Please enter at least one set of credentials.")
        else:
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService
            except ImportError:
                st.error("qiskit-ibm-runtime is not installed. Run: `pip install qiskit-ibm-runtime`")
                st.stop()

            connected = False
            for method, kwargs in connection_attempts:
                try:
                    service = QiskitRuntimeService(**kwargs)
                    st.session_state["ibm_service"] = service
                    st.success(f"Connected via **{method}**")
                    connected = True
                    break
                except Exception as e:
                    st.warning(f"{method}: {e}")

            if not connected:
                st.error("Failed to connect with the provided credentials.")
            else:
                svc = st.session_state["ibm_service"]
                backend_found = False
                for name in PREFERRED_BACKENDS:
                    try:
                        be = svc.backend(name)
                        status = be.status()
                        if status.operational:
                            st.session_state["ibm_backend"] = be
                            st.session_state["ibm_backend_name"] = name
                            st.success(f"Backend: **{name}** ({be.num_qubits}Q, pending jobs: {status.pending_jobs})")
                            backend_found = True
                            break
                    except Exception:
                        continue
                if not backend_found:
                    try:
                        be = svc.least_busy(operational=True, min_num_qubits=5)
                        st.session_state["ibm_backend"] = be
                        st.session_state["ibm_backend_name"] = be.name
                        status = be.status()
                        st.info(f"No preferred backend available. Using least-busy: **{be.name}** ({be.num_qubits}Q, pending: {status.pending_jobs})")
                    except Exception as e:
                        st.error(f"No operational backend found: {e}")

    if st.session_state.get("ibm_backend_name"):
        st.info(f"Currently connected to: **{st.session_state['ibm_backend_name']}**")

    st.markdown("---")

    st.header("2. Run QHED on Real Hardware")
    st.markdown("""
Upload a small image and run QHED edge detection on actual IBM quantum hardware.
**Note:** Real hardware execution is much slower than simulation. A single patch may take
30 seconds to several minutes depending on queue times.
""")

    if demo_mode:
        st.info(
            "In demo mode, hardware execution is disabled. The original image picker "
            "and parameter UI still works for documentation purposes."
        )

    if st.session_state.get("ibm_backend") is None and not demo_mode:
        st.info("Connect to IBM Quantum first (above) to enable hardware execution.")
        st.stop()

    hw_input_image = _select_image()
    if hw_input_image is None:
        st.info("Select or upload an image.")
        st.stop()
    st.image(hw_input_image, caption="Input image", width=250)

    col_hw1, col_hw2, col_hw3 = st.columns(3)
    with col_hw1:
        hw_size_exp = st.selectbox("Resize to", [4, 5, 6], index=0,
                                   format_func=lambda x: f"{2**x}x{2**x}", key="hw_size")
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

    hw_stride = max(hw_patch_size - 2, 1)
    hw_est_patches = int(np.ceil((hw_size - 2) / hw_stride)) ** 2

    backend_name = st.session_state.get("ibm_backend_name") or "(demo)"
    st.markdown(
        f"**Estimated:** {hw_est_patches} patches, {hw_total_qb} qubits/patch, "
        f"{hw_shots} shots/circuit on **{backend_name}**"
    )
    if hw_est_patches > 25:
        st.warning(f"{hw_est_patches} patches will submit many jobs. Consider reducing image size or increasing patch size.")

    if st.button("Run on IBM Quantum Hardware", type="primary", key="hw_run", disabled=demo_mode):
        try:
            from qiskit_ibm_runtime import SamplerV2 as Sampler
            from qiskit import transpile as qk_transpile
            from qiskit import QuantumCircuit
        except ImportError:
            st.error("qiskit-ibm-runtime is required. Install with: pip install qiskit-ibm-runtime")
            st.stop()

        gray = load_image_from_array(hw_input_image, resize=(hw_size, hw_size))
        backend = st.session_state["ibm_backend"]

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
        interior_mask[0, :] = 0; interior_mask[-1, :] = 0
        interior_mask[:, 0] = 0; interior_mask[:, -1] = 0

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

                edge_results = {}
                for label, img_data in [("h", patch), ("v", patch.T)]:
                    norm = amplitude_encode(img_data)
                    if norm is None:
                        edge_results[label] = np.zeros(total_pixels)
                        continue
                    if len(norm) < target_len:
                        norm = np.pad(norm, (0, target_len - len(norm)))

                    qc = QuantumCircuit(total_qb)
                    qc.initialize(norm.tolist(), range(1, total_qb))
                    qc.h(0)
                    qc.compose(D2n_1_circuit(total_qb), range(total_qb), inplace=True)
                    qc.h(0)
                    qc.measure_all()

                    qc_t = qk_transpile(qc, backend=backend, optimization_level=2)

                    try:
                        job = sampler.run([qc_t], shots=hw_shots)
                        result = job.result()
                        pub_result = result[0]
                        counts = pub_result.data.meas.get_counts()
                    except Exception as e:
                        st.warning(f"Patch ({r},{c}) {label}: {e}")
                        edge_results[label] = np.zeros(total_pixels)
                        continue

                    edge = np.zeros(total_pixels)
                    for i in range(total_pixels):
                        key = format(2 * i + 1, f"0{total_qb}b")
                        edge[i] = counts.get(key, 0)
                    edge_results[label] = edge

                row_dim, col_dim = patch.shape
                edge_h = edge_results["h"][:row_dim * col_dim].reshape(row_dim, col_dim)
                edge_v = edge_results["v"][:col_dim * row_dim].reshape(col_dim, row_dim).T
                combined = edge_h + edge_v

                mean_val = np.mean(combined[combined > 0]) if np.any(combined > 0) else 0
                thr = mean_val * 0.5
                edge_binary = (combined > thr).astype(np.float64)
                edge_binary = boundary_zero(edge_binary)

                result_img[r:r + width_patch, c:c + width_patch] += edge_binary
                count_img[r:r + width_patch, c:c + width_patch] += interior_mask

                current += 1
                elapsed = time.time() - start_time
                eta = (elapsed / current) * (total_patches - current) if current > 0 else 0
                progress.progress(
                    current / total_patches,
                    text=f"Patch {current}/{total_patches} | Elapsed: {elapsed:.0f}s | ETA: {eta:.0f}s",
                )

        count_img[count_img == 0] = 1
        hw_result = (result_img / count_img >= 0.5).astype(np.uint8)
        total_time = time.time() - start_time

        progress.progress(1.0, text=f"Done! Total: {total_time:.1f}s")

        st.session_state["ibm_hw_result"] = hw_result
        st.session_state["ibm_hw_gray"] = gray
        st.session_state["ibm_hw_time"] = total_time
        st.session_state["ibm_hw_patches"] = total_patches

    if st.session_state.get("ibm_hw_result") is not None:
        st.header("3. Results")
        hw_res = st.session_state["ibm_hw_result"]
        hw_gray = st.session_state["ibm_hw_gray"]
        hw_time = st.session_state["ibm_hw_time"]
        hw_np = st.session_state["ibm_hw_patches"]

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Original**")
            st.image(hw_gray, clamp=True, use_container_width=True)
        with col_r2:
            st.markdown(f"**QHED on {st.session_state['ibm_backend_name']}** ({hw_np} patches, {hw_time:.1f}s)")
            st.image(hw_res.astype(float), clamp=True, use_container_width=True)

        if st.button("Compare with Simulation", key="hw_compare"):
            sim_progress = st.progress(0, text="Running simulation...")
            sim_start = time.time()
            sim_result, sim_n = edge_detection_stride(
                hw_gray,
                width_qb=st.session_state.get("hw_patch", 3),
                thr_ratio=0.7,
                stride_mode="with_restoration",
                patch_boundary_zero=True,
                progress_callback=lambda c, t: sim_progress.progress(c / t, text=f"Sim: {c}/{t}"),
            )
            sim_time = time.time() - sim_start
            sim_progress.progress(1.0, text="Done!")

            fig_cmp, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(hw_gray, cmap="gray"); axes[0].set_title("Original"); axes[0].axis("off")
            axes[1].imshow(sim_result, cmap="gray"); axes[1].set_title(f"Simulation ({sim_n} patches, {sim_time:.2f}s)"); axes[1].axis("off")
            axes[2].imshow(hw_res, cmap="gray")
            axes[2].set_title(f"IBM Hardware ({hw_np} patches, {hw_time:.1f}s)\n{st.session_state['ibm_backend_name']}")
            axes[2].axis("off")
            plt.tight_layout()
            st.pyplot(fig_cmp)

            st.download_button("Download comparison", fig_to_bytes(fig_cmp, dpi=200),
                               file_name="qhed_hw_vs_sim.png", mime="image/png")
            plt.close(fig_cmp)

        st.download_button(
            "Download hardware result",
            img_to_bytes(hw_res),
            file_name=f"qhed_{st.session_state['ibm_backend_name']}.png",
            mime="image/png",
            key="hw_download",
        )
