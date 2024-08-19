from qiskit.circuit.library import PhaseOracle
from qiskit_algorithms import Grover, AmplificationProblem

from qiskit import QuantumCircuit, transpile

from qiskit_ibm_runtime.ibm_backend import Backend

from qiskit_ibm_runtime.fake_provider.backends import FakeTorino

import utils

from qiskit_aer import AerSimulator

from qiskit.result.result import Result

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
    boolean_expr = 'q0 & ~q1 & ~q2 & q3' # q0 top-most => lsb
    oracle = PhaseOracle(boolean_expr)
    good_states = phase_oracle_solutions(oracle)
    print(good_states)


def get_circuit() -> QuantumCircuit:
    """
    Returns the quantum circuit target for the experiment
    """
    boolean_expr = 'q0 & ~q1 & ~q2 & q3' # q0 top-most => least significant qubit (lsq)
    oracle: QuantumCircuit = PhaseOracle(boolean_expr)
    problem = AmplificationProblem(oracle)

    num_known_solutions = 2
    optimal_num_iterations = Grover.optimal_num_iterations(
        num_solutions=num_known_solutions,
        num_qubits=oracle.num_qubits)

    grover = Grover(iterations=optimal_num_iterations)

    return grover.construct_circuit(problem, measurement=True)


def run_experiment(
        experiment_id: str,
        circuit: QuantumCircuit,
        transpiler_options: dict):
    backend: Backend = transpiler_options['backend']

    transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)

    result: Result = backend \
        .run(transpiled_circuit, shots=4096) \
        .result()

    utils.draw(transpiled_circuit, experiment_id)
    utils.plot(result.get_counts(), experiment_id)
    utils.write_results_json(result.get_counts(), experiment_id)

    return result


def main_experiments():
    circuit = get_circuit()
    backend = FakeTorino()

    simulator = AerSimulator.from_backend(backend)
    simulator.set_options(method='statevector', noise_model=None)
    ideal_experiment = {
        'experiment_id': 'ideal',
        'circuit': circuit,
        'transpiler_options': {
            'backend': simulator
        }
    }
    run_experiment(**ideal_experiment)

    noisy_experiment = {
        'experiment_id': 'noisy',
        'circuit': circuit,
        'transpiler_options': {
            'backend': backend
        }
    }
    run_experiment(**noisy_experiment)


if __name__ == '__main__':
    # main()
    # test_phase_oracle_solutions()
    # main_with_noise()
    main_experiments()
    pass
