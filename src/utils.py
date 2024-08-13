"""
Helper functions
"""
import simplejson
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram


def draw(circuit: QuantumCircuit, file_name: str):
    """
    Draws the circuit into a PNG file
    """
    params = {
        'initial_state': True,
        'output': "mpl",
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


def write_results_json(counts: dict, script_name: str, sufiix: str):
    """
    write counts into file as JSON
    """
    file_name = f'{script_name}.counts{sufiix}.txt'
    with open(file_name, 'w', encoding='utf-8') as file:
        simplejson.dump(counts, fp=file, indent=4, sort_keys=True)
