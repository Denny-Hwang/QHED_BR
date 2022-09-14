# Importing standard Qiskit libraries and configuring account
from qiskit import *
from qiskit import IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.jupyter import *
from qiskit.visualization import *

from basicFunctions import amplitude_encode

import numpy as np

from matplotlib import style
style.use('bmh')

def QHED_MN(image, thr_ratio=0.7, circuit_display=True, plot_ED_result=True):
    '''

    '''
    row, col = image.shape[0], image.shape[1]
    qb_size = np.int(np.ceil(np.log2(row * col)))

    # 1) Data encoding
    # Horizontal: Original image
    image_norm_h = amplitude_encode(image)
    # Vertical: Transpose of Original image
    image_norm_v = amplitude_encode(image.T)

    if len(np.unique(image_norm_h)) == 1:
        return image

    else:
        # 2) Generate quantum circuit
        # Initialize the number of qubits
        data_qb = qb_size
        anc_qb = 1
        total_qb = data_qb + anc_qb

        # Initialize the amplitude permutation unitary
        D2n_1 = np.roll(np.identity(2 ** total_qb), 1, axis=1)

        # Create the circuit for horizontal scan
        qc_h = QuantumCircuit(total_qb)
        qc_h.initialize(image_norm_h, range(1, total_qb))
        qc_h.barrier()
        qc_h.h(0)
        qc_h.unitary(D2n_1, range(total_qb))
        qc_h.h(0)
        qc_h.barrier()
        if circuit_display:
            display(qc_h.draw('mpl', fold=-1))

        # Create the circuit for vertical scan
        qc_v = QuantumCircuit(total_qb)
        qc_v.initialize(image_norm_v, range(1, total_qb))
        qc_v.barrier()
        qc_v.h(0)
        qc_v.unitary(D2n_1, range(total_qb))
        qc_v.h(0)
        qc_v.barrier()
        if circuit_display:
            display(qc_v.draw('mpl', fold=-1))

        # Combine both circuits into a single list
        circ_list = [qc_h, qc_v]

        # 3) Measure the state
        # Simulating the cirucits
        back = Aer.get_backend('statevector_simulator')
        results = execute(circ_list, backend=back).result()
        sim_sv_h = results.get_statevector(qc_h)
        sim_sv_v = results.get_statevector(qc_v)

        # 4) Result postprocessing in classical computer
        # Defining a lambda function for thresholding to binary values
        thr = (np.mean(sim_sv_h) + np.mean(sim_sv_v)) / 2 * thr_ratio
        threshold = lambda amp: (np.abs(amp) > thr)

        # Filter and extract the counts for odd-numbered states
        # and make the full edge-detected image by adding horizontal and vertical scans
        edge_scan_sim_h = np.abs(
            np.array([1 if threshold(sim_sv_h[2 * i + 1].real) else 0 for i in range(2 ** data_qb)]))
        edge_scan_sim_h = edge_scan_sim_h[:row * col].reshape(row, col)

        edge_scan_sim_v = np.abs(
            np.array([1 if threshold(sim_sv_v[2 * i + 1].real) else 0 for i in range(2 ** data_qb)]))
        edge_scan_sim_v = edge_scan_sim_v[:row * col].reshape(row, col).T

        if edge_scan_sim_h.shape == edge_scan_sim_v.shape:
            edge_detected_sim = edge_scan_sim_h | edge_scan_sim_v
        else:
            edge_detected_sim = edge_scan_sim_h

        if plot_ED_result:
            # Plotting the Horizontal and vertical scans
            plot_image(edge_scan_sim_h, 'Horizontal scan output')
            plot_image(edge_scan_sim_v, 'Vertical scan output')

            plot_image(image, 'Original image')
            plot_image(edge_detected_sim, 'Edge Detected image')

        return edge_detected_sim

