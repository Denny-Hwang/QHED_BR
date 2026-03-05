"""Quantum Hadamard Edge Detection (QHED) with Boundary Restoration.

Compatible with Qiskit 2.x and qiskit-aer.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from basicFunctions import amplitude_encode, boundary_zero


# ---------------------------------------------------------------------------
# Core QHED using statevector simulation
# ---------------------------------------------------------------------------

def QHED(image, thr_ratio=0.7):
    """Run QHED on a small square image patch using statevector simulation.

    Parameters
    ----------
    image : np.ndarray
        2D grayscale image (values in [0, 1]), shape must be power-of-2 square.
    thr_ratio : float
        Threshold ratio for binarising edge amplitudes.

    Returns
    -------
    edge_detected : np.ndarray
        Binary edge-detected image (same shape as input).
    """
    row, col = image.shape
    total_pixels = row * col
    data_qb = int(np.ceil(np.log2(total_pixels)))
    anc_qb = 1
    total_qb = data_qb + anc_qb

    # Amplitude encode
    image_norm_h = amplitude_encode(image)
    image_norm_v = amplitude_encode(image.T)

    if image_norm_h is None:
        return np.zeros_like(image)

    # Pad to 2^data_qb if needed
    target_len = 2 ** data_qb
    if len(image_norm_h) < target_len:
        image_norm_h = np.pad(image_norm_h, (0, target_len - len(image_norm_h)))
    if image_norm_v is not None and len(image_norm_v) < target_len:
        image_norm_v = np.pad(image_norm_v, (0, target_len - len(image_norm_v)))

    # Amplitude permutation unitary (cyclic shift)
    D2n_1 = np.roll(np.identity(2 ** total_qb), 1, axis=1)

    results = {}
    for label, norm_data in [('h', image_norm_h), ('v', image_norm_v)]:
        if norm_data is None:
            results[label] = np.zeros(row * col)
            continue

        qc = QuantumCircuit(total_qb)
        qc.initialize(norm_data.tolist(), range(1, total_qb))
        qc.h(0)
        qc.unitary(D2n_1, range(total_qb))
        qc.h(0)

        sv = np.asarray(Statevector.from_instruction(qc))

        # Extract odd-indexed amplitudes (edge information)
        edge_amps = np.abs(np.real(sv[1::2]))[:total_pixels]
        results[label] = edge_amps

    # Threshold
    mean_amp = (np.mean(results['h']) + np.mean(results['v'])) / 2
    thr = mean_amp * thr_ratio

    edge_h = (results['h'] > thr).astype(np.uint8).reshape(row, col)
    edge_v = (results['v'] > thr).astype(np.uint8).reshape(col, row).T

    return edge_h | edge_v


def build_qhed_circuit(image, scan='horizontal'):
    """Build a QHED circuit for visualization purposes.

    Returns the QuantumCircuit (without save_statevector).
    """
    if scan == 'vertical':
        image = image.T

    row, col = image.shape
    total_pixels = row * col
    data_qb = int(np.ceil(np.log2(total_pixels)))
    total_qb = data_qb + 1

    norm_data = amplitude_encode(image)
    if norm_data is None:
        return None

    target_len = 2 ** data_qb
    if len(norm_data) < target_len:
        norm_data = np.pad(norm_data, (0, target_len - len(norm_data)))

    D2n_1 = np.roll(np.identity(2 ** total_qb), 1, axis=1)

    ancilla = QuantumRegister(1, 'ancilla')
    data = QuantumRegister(data_qb, 'pixel')
    cr = ClassicalRegister(total_qb, 'meas')
    qc = QuantumCircuit(ancilla, data, cr)

    qc.initialize(norm_data.tolist(), range(1, total_qb))
    qc.barrier()
    qc.h(0)
    qc.unitary(D2n_1, range(total_qb), label='D_{2n-1}')
    qc.h(0)
    qc.barrier()
    qc.measure(range(total_qb), range(total_qb))

    return qc


# ---------------------------------------------------------------------------
# QHED with QASM (shot-based) simulation
# ---------------------------------------------------------------------------

def QHED_qasm(image, thr_ratio=0.7, shots=10000):
    """Run QHED using QASM (shot-based) simulation.

    Returns edge-detected image as float array (counts-based).
    """
    row, col = image.shape
    total_pixels = row * col
    data_qb = int(np.ceil(np.log2(total_pixels)))
    total_qb = data_qb + 1

    image_norm_h = amplitude_encode(image)
    image_norm_v = amplitude_encode(image.T)

    if image_norm_h is None:
        return np.zeros_like(image)

    target_len = 2 ** data_qb
    if len(image_norm_h) < target_len:
        image_norm_h = np.pad(image_norm_h, (0, target_len - len(image_norm_h)))
    if image_norm_v is not None and len(image_norm_v) < target_len:
        image_norm_v = np.pad(image_norm_v, (0, target_len - len(image_norm_v)))

    D2n_1 = np.roll(np.identity(2 ** total_qb), 1, axis=1)
    backend = AerSimulator()

    results = {}
    for label, norm_data in [('h', image_norm_h), ('v', image_norm_v)]:
        if norm_data is None:
            results[label] = np.zeros(total_pixels)
            continue

        qc = QuantumCircuit(total_qb)
        qc.initialize(norm_data.tolist(), range(1, total_qb))
        qc.barrier()
        qc.h(0)
        qc.unitary(D2n_1, range(total_qb))
        qc.h(0)
        qc.measure_all()

        qc_t = transpile(qc, backend=backend, optimization_level=2)
        job = backend.run(qc_t, shots=shots)
        counts = job.result().get_counts()

        edge = np.zeros(total_pixels)
        for i in range(total_pixels):
            key = format(2 * i + 1, f'0{total_qb}b')
            edge[i] = counts.get(key, 0)
        results[label] = edge

    edge_h = results['h'].reshape(row, col)
    edge_v = results['v'].reshape(col, row).T
    combined = edge_h + edge_v

    return combined


# ---------------------------------------------------------------------------
# Patch-based QHED for large images (with Boundary Restoration)
# ---------------------------------------------------------------------------

def edge_detection_stride(input_img, width_qb=2, thr_ratio=0.5,
                          stride_mode='with_restoration',
                          patch_boundary_zero=True,
                          progress_callback=None):
    """Apply QHED to a large image using sliding patches.

    Parameters
    ----------
    input_img : np.ndarray
        2D grayscale image, normalized [0, 1].
    width_qb : int
        Number of qubits for one dimension of patch (patch size = 2^width_qb x 2^width_qb).
    thr_ratio : float
        Threshold ratio for edge binarisation.
    stride_mode : str
        'without_restoration' - non-overlapping patches (information loss at boundaries).
        'with_restoration' - overlapping patches with majority voting to restore boundaries.
    patch_boundary_zero : bool
        Whether to zero boundaries of each patch before accumulation.
    progress_callback : callable or None
        Function(current, total) called to report progress.

    Returns
    -------
    result_img : np.ndarray
        Binary edge-detected image.
    n_patches : int
        Number of patches processed.
    """
    width_patch = 2 ** width_qb
    h, w = input_img.shape

    if stride_mode == 'with_restoration':
        stride = width_patch - 1  # overlap by 1 pixel row/col
    else:
        stride = width_patch  # no overlap

    # Compute patch positions
    row_positions = list(range(0, h - width_patch + 1, stride))
    if row_positions[-1] + width_patch < h:
        row_positions.append(h - width_patch)
    col_positions = list(range(0, w - width_patch + 1, stride))
    if col_positions[-1] + width_patch < w:
        col_positions.append(w - width_patch)

    result_img = np.zeros((h, w), dtype=np.float64)
    count_img = np.zeros((h, w), dtype=np.float64)

    total_patches = len(row_positions) * len(col_positions)
    current = 0

    for r in row_positions:
        for c in col_positions:
            patch = input_img[r:r + width_patch, c:c + width_patch]
            edge_result = QHED(patch, thr_ratio=thr_ratio)

            if patch_boundary_zero:
                edge_result = boundary_zero(edge_result)

            result_img[r:r + width_patch, c:c + width_patch] += edge_result.astype(np.float64)
            count_img[r:r + width_patch, c:c + width_patch] += 1.0

            current += 1
            if progress_callback:
                progress_callback(current, total_patches)

    # Majority voting: if more than half of overlapping patches detected edge, keep it
    count_img[count_img == 0] = 1
    result_img = (result_img / count_img >= 0.5).astype(np.uint8)

    return result_img, total_patches
