"""Regression tests for the QHED algorithm and the cyclic-shift circuit.

Run with::

    python -m pytest tests/

These tests are deliberately lightweight (a few seconds total) so they can
run in CI without a quantum simulator backend beyond Aer's statevector.
"""

import os
import sys

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from basicFunctions import amplitude_encode, boundary_zero  # noqa: E402
from qhed import (  # noqa: E402
    D2n_1_circuit,
    QHED,
    build_qhed_circuit,
    edge_detection_stride,
)


# ---------------------------------------------------------------------------
# D_{2n-1} circuit
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [2, 3, 4, 5])
def test_D2n_1_circuit_matches_dense_unitary(n):
    """Gate-level D_{2n-1} must equal the np.roll dense unitary used in the
    original implementation (up to floating-point precision)."""
    dense = np.roll(np.identity(2 ** n), 1, axis=1)
    gate_op = Operator(D2n_1_circuit(n)).data
    assert np.allclose(gate_op, dense, atol=1e-10)


@pytest.mark.parametrize("n", [3, 4])
def test_D2n_1_circuit_is_cyclic_shift(n):
    """Applied to |x>, the circuit produces |x - 1 mod 2^n>."""
    dim = 2 ** n
    for x in range(dim):
        qc = QuantumCircuit(n)
        # prepare |x> via little-endian bit injection
        for i in range(n):
            if (x >> i) & 1:
                qc.x(i)
        qc.compose(D2n_1_circuit(n), range(n), inplace=True)
        sv = np.asarray(Statevector.from_instruction(qc))
        target = (x - 1) % dim
        assert np.isclose(abs(sv[target]), 1.0, atol=1e-10)


# ---------------------------------------------------------------------------
# amplitude_encode
# ---------------------------------------------------------------------------

def test_amplitude_encode_normalised():
    img = np.array([[0.1, 0.2], [0.3, 0.4]])
    v = amplitude_encode(img)
    assert v is not None
    assert np.isclose(np.linalg.norm(v), 1.0)


def test_amplitude_encode_uniform_returns_none():
    """A constant patch has no edges; encoder signals this with None."""
    img = np.full((4, 4), 0.5)
    assert amplitude_encode(img) is None


# ---------------------------------------------------------------------------
# boundary_zero
# ---------------------------------------------------------------------------

def test_boundary_zero_outer_ring():
    img = np.ones((4, 4))
    out = boundary_zero(img)
    assert (out[0, :] == 0).all()
    assert (out[-1, :] == 0).all()
    assert (out[:, 0] == 0).all()
    assert (out[:, -1] == 0).all()
    assert (out[1:-1, 1:-1] == 1).all()


# ---------------------------------------------------------------------------
# QHED on a known image
# ---------------------------------------------------------------------------

def test_QHED_detects_vertical_step():
    """A 4x4 image with a sharp vertical step must produce non-zero edges."""
    img = np.zeros((4, 4))
    img[:, 2:] = 1.0
    edges = QHED(img, thr_ratio=0.5)
    assert edges.shape == img.shape
    # the step at column 1->2 (and the wrap-around) must light up at least
    # one pixel
    assert edges.sum() > 0


def test_QHED_returns_zero_for_uniform_image():
    img = np.full((4, 4), 0.5)
    edges = QHED(img, thr_ratio=0.5)
    assert edges.shape == img.shape
    assert edges.sum() == 0


def test_QHED_signature_back_compat():
    """The deprecated D2n_1 keyword must still be accepted (and ignored)."""
    img = np.zeros((4, 4))
    img[:, 2:] = 1.0
    edges_no_kwarg = QHED(img, thr_ratio=0.5)
    edges_with_kwarg = QHED(img, thr_ratio=0.5, D2n_1="anything")
    assert np.array_equal(edges_no_kwarg, edges_with_kwarg)


# ---------------------------------------------------------------------------
# build_qhed_circuit (visualisation helper)
# ---------------------------------------------------------------------------

def test_build_qhed_circuit_returns_circuit():
    img = np.array([[0.0, 1.0], [1.0, 0.0]])
    qc = build_qhed_circuit(img)
    assert isinstance(qc, QuantumCircuit)
    # 2x2 image -> 2 data qubits + 1 ancilla
    assert qc.num_qubits == 3


def test_build_qhed_circuit_uniform_returns_none():
    img = np.full((2, 2), 0.5)
    assert build_qhed_circuit(img) is None


# ---------------------------------------------------------------------------
# edge_detection_stride (patch-based)
# ---------------------------------------------------------------------------

def test_edge_detection_stride_shape_preserved():
    rng = np.random.default_rng(42)
    img = rng.random((16, 16))
    out, n_patches = edge_detection_stride(
        img, width_qb=3, thr_ratio=0.5,
        stride_mode='with_restoration', patch_boundary_zero=True,
    )
    assert out.shape == img.shape
    assert n_patches >= 1
    assert out.dtype == np.uint8


def test_edge_detection_stride_modes_differ():
    """With and without restoration should produce different patch counts."""
    rng = np.random.default_rng(0)
    img = rng.random((16, 16))
    _, n_no_br = edge_detection_stride(
        img, width_qb=3, stride_mode='without_restoration'
    )
    _, n_br = edge_detection_stride(
        img, width_qb=3, stride_mode='with_restoration'
    )
    assert n_br >= n_no_br


def test_edge_detection_stride_rejects_oversized_patch():
    img = np.zeros((4, 4))
    with pytest.raises(ValueError):
        edge_detection_stride(img, width_qb=3)  # 8x8 patch on 4x4 image
