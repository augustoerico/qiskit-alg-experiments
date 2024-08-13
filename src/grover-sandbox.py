from qiskit.circuit.library import PhaseOracle
from qiskit.primitives import Sampler
from qiskit_algorithms import Grover, AmplificationProblem

import utils

def main():
    boolean_expr = '(q0 & q1) | (~q2 & q3)' # q0 top-most => lsb
    oracle = PhaseOracle(boolean_expr)
    oracle.barrier()

    bitstrings = [
        f'{i:04b}'
        for i in range(2 ** 4)
    ]
    # print(bitstrings)

    results = {
        i: oracle.evaluate_bitstring(i)
        for i in bitstrings
    }
    # print(results)

    good_states = [
        k
        for k, v in results.items()
        if v is True
    ]
    # print(good_states)

    def is_good_state(state: str) -> bool:
        return state in good_states

    problem = AmplificationProblem(
        oracle,
        is_good_state=is_good_state
    )

    utils.draw(problem.grover_operator.decompose(), 'amp-problem-op')

    optimal_num_iterations = Grover.optimal_num_iterations(7, 4)
    
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
