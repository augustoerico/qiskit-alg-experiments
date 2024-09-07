from typing import Tuple

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_ibm_runtime.ibm_backend import Backend

import utils
from scenario import Scenario
from runner import ScenarioRunner

from folders import create_artifacts_folder

from qiskit.qasm3 import dump as qasm3_dump


class Grover9qExperiment:

    id: str
    reference_backend: Backend
    transpiled_circuit: QuantumCircuit
    scenarios: Tuple[Scenario, Scenario]

    def __init__(
        self, id: str, reference_backend: Backend,
        scenarios: list[Scenario]):
        self.id = id
        self.reference_backend = reference_backend
        self.scenarios = scenarios
        self.transpiled_circuit = self.get_transpiled_circuit()

    @utils.print_exec_time
    def get_transpiled_circuit(self) -> QuantumCircuit:
        boolean_expr = '(~q0 & ~q1 & ~q2 & q3 & q4 & q5 & ~q6 & ~q7 & ~q8) ' +\
              '| (~q0 & q1 & ~q2 & ~q3 & q4 & ~q5 & ~q6 & q7 & ~q8)'  # q0 top-most: least significant qubit
        oracle: QuantumCircuit = PhaseOracle(boolean_expr)
        problem = AmplificationProblem(oracle)

        num_known_solutions = 2
        optimal_num_iterations = Grover.optimal_num_iterations(
            num_solutions=num_known_solutions,
            num_qubits=oracle.num_qubits)
        
        circuit = Grover(iterations=optimal_num_iterations) \
            .construct_circuit(problem, measurement=True)

        transpiled_circuit = transpile(
            circuit, backend=self.reference_backend, optimization_level=3)
        self.transpiled_circuit = transpiled_circuit
        return transpiled_circuit

    def run_scenarios(self):
        artifacts_folder_path = create_artifacts_folder(self.id)

        circuit = self.transpiled_circuit
        circuit_qasm_file_name = f'{artifacts_folder_path}/{self.id}.qasm'
        
        # [TODO] refactor into a utils function
        with open(circuit_qasm_file_name, 'w', encoding='utf-8') as file:
            qasm3_dump(circuit, file)

        for scenario in self.scenarios:
            runner = ScenarioRunner(
                circuit=circuit,
                scenario=scenario)
            runner_results = runner.run()
            results_file_name = f'{artifacts_folder_path}/scenario-{scenario["id"]}'
            utils.write_job_results_json(runner_results, results_file_name)
            utils.write_results_csv(runner_results.get_counts(), results_file_name)


def main():
    from os import environ
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_ibm_runtime.fake_provider.backends import FakeTorino

    reference_backend = FakeTorino()

    noisy_backend = reference_backend
    ideal_backend = AerSimulator.from_backend(reference_backend)
    ideal_backend.set_options(method='statevector', noise_model=None)
    scenarios = [
        Scenario(id='noisy', backend=noisy_backend),
        Scenario(id='ideal', backend=ideal_backend)
    ]
    grover_experiment = Grover9qExperiment(
        id='grover-9q',
        reference_backend=reference_backend,
        scenarios=scenarios)
    grover_experiment.run_scenarios()


if __name__ == '__main__':
    main()
