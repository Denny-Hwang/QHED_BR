"""Page 2 — QHED Circuit Explained."""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from basicFunctions import amplitude_encode
from qhed import build_qhed_circuit
from ui.helpers import fig_to_bytes


def render() -> None:
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
            circuit_text = qc.draw('text', fold=120)
            st.code(str(circuit_text), language=None)
    else:
        st.warning("Could not build circuit (uniform image).")

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
