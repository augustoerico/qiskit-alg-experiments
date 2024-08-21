from qiskit.circuit.library import PhaseOracle
from qiskit_algorithms import Grover, AmplificationProblem

from qiskit import QuantumCircuit, transpile

from qiskit_ibm_runtime.ibm_backend import Backend

from qiskit_ibm_runtime.fake_provider.backends import FakeTorino

import utils

from qiskit_aer import AerSimulator

from qiskit.result.result import Result

from scipy.stats import ks_2samp, mannwhitneyu, shapiro

from numpy import array
from experiments_engine import run_experiment


def phase_oracle_solutions(oracle: PhaseOracle):
    # generate all binaries from 0 to num_qubits
    num_qubits = oracle.num_qubits
    bitstrings = [
        bin(i)[2:].zfill(num_qubits)
        for i in range(2 ** num_qubits)
    ]
    # print(bitstrings)

    truth_table = {
        i: oracle.evaluate_bitstring(i)
        for i in bitstrings
    }
    # print(truth_table)

    good_states = [
        k
        for k, v in truth_table.items()
        if v is True
    ]
    # print(good_states)

    return good_states


def test_phase_oracle_solutions():
    boolean_expr = '(q0 & ~q1 & ~q2 & q3) | (~q0 & q1 & q2 & ~q3)' # q0 top-most => lsb
    oracle = PhaseOracle(boolean_expr)
    good_states = phase_oracle_solutions(oracle)
    print(good_states)


@utils.print_exec_time
def get_transpiled_grover_circuit(backend: Backend) -> QuantumCircuit:
    """
    Returns the quantum circuit target for the experiment
    """
    boolean_expr = '(q0 & ~q1 & ~q2 & q3) | (~q0 & q1 & q2 & ~q3)' # q0 top-most => least significant qubit (lsq)
    oracle: QuantumCircuit = PhaseOracle(boolean_expr)
    problem = AmplificationProblem(oracle)

    num_known_solutions = 2
    optimal_num_iterations = Grover.optimal_num_iterations(
        num_solutions=num_known_solutions,
        num_qubits=oracle.num_qubits)

    grover_circuit = Grover(iterations=optimal_num_iterations) \
        .construct_circuit(problem, measurement=True)
    
    transpiled_circuit = transpile(
        grover_circuit,backend=backend, optimization_level=3)
    utils.draw(transpiled_circuit, f'grover.{backend.name}')
    
    return transpiled_circuit


@utils.print_exec_time
def run_testing_experiments():
    """
    Runs the experiments in 2 environments and performs
        a 2-sample KS test: Statistical Assertion
    """
    backend = FakeTorino()
    transpiled_circuit = get_transpiled_grover_circuit(backend)

    simulator = AerSimulator.from_backend(backend)
    simulator.set_options(method='statevector', noise_model=None)
    ideal_experiment = {
        'experiment_id': 'grover.ideal',
        'transpiled_circuit': transpiled_circuit,
        'backend': simulator
    }
    ideal_result = run_experiment(**ideal_experiment)
    ideal_result_counts: dict = ideal_result.get_counts()

    noisy_experiment = {
        'experiment_id': 'grover.noisy',
        'transpiled_circuit': transpiled_circuit,
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
    ideal_experiment_data = array(ideal_experiment_data)
    noisy_experiment_data = array(noisy_experiment_data)
    
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


if __name__ == '__main__':
    # test_phase_oracle_solutions()
    run_testing_experiments()
    pass
