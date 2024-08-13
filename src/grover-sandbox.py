from qiskit.circuit.library import PhaseOracle
from qiskit.primitives import Sampler
from qiskit_algorithms import Grover, AmplificationProblem

import utils

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
    boolean_expr = '(q0 & q1) | (~q2 & q3)' # q0 top-most => lsb
    oracle = PhaseOracle(boolean_expr)
    good_states = phase_oracle_solutions(oracle)
    print(good_states)


def main():
    boolean_expr = '(q0 & q1) | (~q2 & q3)' # q0 top-most => lsb
    oracle = PhaseOracle(boolean_expr)
    oracle.barrier()

    problem = AmplificationProblem(
        oracle
    )

    utils.draw(problem.grover_operator.decompose(), 'amp-problem-op')

    num_known_solutions = 7
    optimal_num_iterations = Grover.optimal_num_iterations(
        num_solutions=num_known_solutions,
        num_qubits=oracle.num_qubits)
    
    grover_ideal = Grover(
        iterations=optimal_num_iterations,
        growth_rate=None,
        sample_from_iterations=False,
        sampler=Sampler() # ideal
    )
    result_ideal = grover_ideal.amplify(problem).circuit_results[0]
    utils.plot(result_ideal, "grover-ideal")

    grover_shots = Grover(
        iterations=optimal_num_iterations,
        growth_rate=None,
        sample_from_iterations=None,
        sampler=Sampler(options={"shots": 512, "seed": 123})
    )
    result_shots = grover_shots.amplify(problem).circuit_results[0]
    utils.plot(result_shots, "grover-shots-optimal")


if __name__ == '__main__':
    main()
    # test_phase_oracle_solutions()
    pass
