"""
Deutsch-Jozsa Algorithm Circuit
"""
from numpy import array as numpy_array
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider.backends import FakeTorino
from qiskit_ibm_runtime.ibm_backend import Backend
from scipy.stats import ks_2samp, mannwhitneyu, shapiro

import utils
from experiments_engine import run_experiment
from gates import n_hadamard


def constant_1_oracle(n_qubits: int, initialization = None) -> QuantumCircuit:
    """
    Returns constant function oracle
    """
    qubits = QuantumRegister(n_qubits, name='q')
    q_out = QuantumRegister(1, 'q_out')
    c_out = ClassicalRegister(1, 'c_out')
    circuit = QuantumCircuit(qubits, q_out, c_out, name='oracle')

    if initialization:
        circuit.initialize('0' + initialization)
    circuit.x(q_out)

    return circuit


def balanced_oracle(n_qubits: int, initialization = None) -> QuantumCircuit:
    """
    Returns balanced function oracle
    """
    qubits = QuantumRegister(n_qubits, name='q')
    q_out = QuantumRegister(1, 'q_out')
    c_out = ClassicalRegister(1, 'c_out')
    circuit = QuantumCircuit(qubits, q_out, c_out, name='oracle')
    
    if initialization:
        circuit.initialize('0' + initialization)
    circuit.cx(control_qubit=qubits[-1], target_qubit=q_out)

    return circuit


def deutsch_jozsa_algorithm_circuit(oracle: QuantumCircuit) -> QuantumCircuit:
    """
    Appends Deutsch-Jozsa quantum gates to the oracle circuit
    """
    n_qubits = len(oracle.qubits) - 1

    qubits = QuantumRegister(n_qubits, name='q')
    q_out = QuantumRegister(1, 'q_out')
    c_out = ClassicalRegister(n_qubits, 'c_out')
    circuit = QuantumCircuit(qubits, q_out, c_out, name='oracle')

    initialization = '-' + ('0' * n_qubits) # perform a single query with 0's and
                                            #   | ancilla initialized with '-'
    circuit.initialize(initialization)

    pre_processing_circuit = n_hadamard(n_qubits)
    circuit = circuit.compose(pre_processing_circuit)
    circuit.barrier()

    circuit = circuit.compose(oracle)
    circuit.barrier()

    post_processing_circuit = n_hadamard(n_qubits)
    post_processing_circuit.measure_all()

    circuit = circuit.compose(post_processing_circuit)
    return circuit


@utils.print_exec_time
def get_transpiled_deutsch_jozsa_circuit(
        backend: Backend, f_constant_oracle = True):
    """
    Returns the quantum circuit target for the experiment
    """
    num_qubits = 4
    if f_constant_oracle:
        oracle = constant_1_oracle(num_qubits)
        oracle_type = 'constant-1'
    else:
        oracle = balanced_oracle(num_qubits)
        oracle_type = 'balanced'

    circuit = deutsch_jozsa_algorithm_circuit(oracle)
    
    transpiled_circuit = transpile(
        circuit, backend=backend, optimization_level=3)
    utils.draw(transpiled_circuit,
               f'deutsch-jozsa.{oracle_type}.{backend.name}')
    
    return transpiled_circuit


@utils.print_exec_time
def run_testing_experiments():
    """
    Runs the experiments in 2 environments and performs
        a 2-sample KS test: Statistical Assertion
    """
    backend = FakeTorino()
    transpiled_circuit_f_constant_oracle = \
        get_transpiled_deutsch_jozsa_circuit(backend)

    simulator = AerSimulator.from_backend(backend)
    simulator.set_options(method='statevector', noise_model=None)
    ideal_experiment = {
        'experiment_id': 'deutsch-jozsa.ideal',
        'transpiled_circuit': transpiled_circuit_f_constant_oracle,
        'backend': simulator
    }
    ideal_result = run_experiment(**ideal_experiment)
    ideal_result_counts: dict = ideal_result.get_counts()

    noisy_experiment = {
        'experiment_id': 'deutsch-jozsa.noisy',
        'transpiled_circuit': transpiled_circuit_f_constant_oracle,
        'backend': backend
    }
    noisy_result = run_experiment(**noisy_experiment)
    noisy_result_counts: dict = noisy_result.get_counts()

    observed_outputs = set(
        list(ideal_result_counts.keys()) +
        list(noisy_result_counts.keys())
    )

    ideal_experiment_data: list[int] = []
    noisy_experiment_data: list[int] = []
    for o in observed_outputs:
        ideal_experiment_data.append(ideal_result_counts.get(o, 0))
        noisy_experiment_data.append(noisy_result_counts.get(o, 0))
    ideal_experiment_data = numpy_array(ideal_experiment_data)
    noisy_experiment_data = numpy_array(noisy_experiment_data)
    
    # test if it's a normal distribution
    # Shapiro H0: the data is normally distributed
    _, pvalue = shapiro(ideal_experiment_data)
    print(f'Shapiro p-value: {pvalue}') # small p-value -> reject H0 -> not normal dist.

    # H0: the 2 samples are drawn from the same distribution
    ks_result = ks_2samp(ideal_experiment_data, noisy_experiment_data)
    print(type(ks_result))
    print(ks_result.pvalue) # small p-value -> strong evidence to *reject* H0

    mw_result = mannwhitneyu(ideal_experiment_data, noisy_experiment_data)
    print(type(mw_result))
    print(mw_result.pvalue)

def main():
    """
    runs experiments
    """
    run_testing_experiments()

if __name__ == '__main__':
    main()

