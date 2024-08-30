from typing import Tuple

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_ibm_runtime.ibm_backend import Backend

import utils
from scenario import Scenario
from statistical_test import StatisticalTestsResultsByType

from folders import create_artifacts_folder


class GroverStatExperiment:

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
        boolean_expr = '(q0 & ~q1 & ~q2 & q3) | (~q0 & q1 & q2 & ~q3)' # q0 top-most => least significant qubit (lsq)
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
        # runner = ScenarioRunner(
        #     transpiled_circuit=self.get_transpiled_circuit())
        # runner_results = [
        #     runner.run()
        #     for s in self.scenarios
        # ]

        artifacts_folder_path = create_artifacts_folder()
        circuit_draw_file_name = f'{artifacts_folder_path}/{self.id}'
        utils.draw(self.transpiled_circuit, circuit_draw_file_name)
        # [
        #     self.generate_scenario_artifacts(r)
        #     for r in runner_results
        # ]

        # self.scenarios_results = stat_test_results(
        #     runner_results[0]['result'], runner_results[1]['result'])

    def generate_scenario_artifacts(
            self, runner_result: StatisticalTestsResultsByType):
        counts = runner_result['result'].get_counts()
        scenario = runner_result['scenario']
        file_name = f'{self.id}.{scenario.id}'
        utils.write_results_json(counts, file_name)
        utils.write_results_csv(counts, file_name)
        utils.plot(counts, file_name)
