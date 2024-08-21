"""
Helper functions
"""
from time import time

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

def write_results_csv(counts: dict, file_name: str):
    """
    write counts into file as CSV
    """
    header = 'cbits,counts\n'
    lines = ''.join([
        f'{cbits},{count}\n'
        for cbits, count in sorted(counts.items())
    ])
    content = header + lines
    
    file_name = f'{file_name}.counts.csv'
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)


def print_exec_time(function):
    def wrapper(*args, **kwargs):
        start_time = time()
        result = function(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f'{function.__name__}: {elapsed_time}s')
        return result
    return wrapper
