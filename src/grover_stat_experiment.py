from typing import TypedDict, Tuple

from numpy import array as np_array
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit.result.result import Result
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_ibm_runtime.ibm_backend import Backend
from scipy.stats import shapiro, ks_2samp, mannwhitneyu, wilcoxon

import utils
from runner import ScenarioRunner
from scenario import Scenario
from statistical_test import StatisticalTestsResultsByType

from unittest import TestCase


class GroverStatExperiment:

    id: str
    transpiled_circuit: QuantumCircuit
    scenarios: Tuple[Scenario, Scenario]
    report: Report

    def __init__(
        self, id: str, reference_backend: Backend,
                 scenarios: list[Scenario]):
        self._experiment_id = experiment_id
        self._reference_backend = reference_backend
        if len(scenarios) != 2: # for now, only 2 scenarios
            raise RuntimeError('Please provide exactly 2 scenarios')
        self._scenarios = scenarios

    def get_report(self) -> Report:
        return self.report

    @utils.print_exec_time
    def _get_transpiled_circuit(self) -> QuantumCircuit:
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
            circuit, backend=self._reference_backend, optimization_level=3)
        return transpiled_circuit

    def run_scenarios(self):
        runner = ScenarioRunner(transpiled_circuit=self._get_transpiled_circuit())
        runner_results = [
            runner._run_one(s)
            for s in self._scenarios
        ]

        utils.draw(runner._transpiled_circuit, self._experiment_id)
        [
            self._generate_scenario_artifacts(r)
            for r in runner_results
        ]

        # for now, it's given that we process 2 scenarios
        stat_test_results(
            runner_results[0]['result'], runner_results[1]['result'])

    def _generate_scenario_artifacts(self, runner_result: ScenarioRunnerResult):
        counts = runner_result['result'].get_counts()
        scenario = runner_result['scenario']
        file_name = f'{self._experiment_id}.{scenario._scenario_id}'
        utils.write_results_json(counts, file_name)
        utils.write_results_csv(counts, file_name)
        utils.plot(counts, file_name)
