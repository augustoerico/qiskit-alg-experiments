"""
Helper functions
"""
from time import time

import simplejson
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime.ibm_backend import Backend


def draw(circuit: QuantumCircuit, file_name: str):
    """
    Draws the circuit into a PNG file
    """
    params = {
        'initial_state': True,
        'output': "mpl",
        'idle_wires': False,
        'filename': f'{file_name}.circuit.png',
    }
    circuit.draw(**params)


def plot(counts: dict, file_name: str, legend = None):
    """
    Plot histogram into a PNG file
    """
    plot_histogram(
        counts,
        figsize=(15, 20),
        title=file_name,
        legend=legend,
        filename=f'{file_name}.histogram.png'
    )


def write_results_json(counts: dict, file_name: str):
    """
    write counts into file as JSON
    """
    file_name = f'{file_name}.counts.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        simplejson.dump(counts, fp=file, indent=4, sort_keys=True)

def simulate(
        circuit: QuantumCircuit,
        backend: Backend,
        shots = 1024):
    transpiled_circuit = transpile(circuit, backend=backend, optimization_level=2)
    draw(transpiled_circuit, 'transpiled')
    counts = backend \
        .run(transpiled_circuit, shots=shots) \
        .result() \
        .get_counts()
    return counts

def print_exec_time(function):
    def wrapper(*args, **kwargs):
        start_time = time()
        result = function(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f'{function.__name__}: {elapsed_time}s')
        return result
    return wrapper
