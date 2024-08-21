from numpy import array as np_array
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit.result.result import Result
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_ibm_runtime.ibm_backend import Backend
from scipy.stats import shapiro, ks_2samp, mannwhitneyu

import utils
from runner import Runner, RunnerResult
from scenario import Scenario


def stat_test_results(result_1: Result, result_2: Result):
    result_1_counts: dict = result_1.get_counts()
    result_2_counts: dict = result_2.get_counts()
    observed_outputs = set(
        list(result_1_counts.keys()) +
        list(result_2_counts.keys())
    )

    result_1_data: list[int] = []
    result_2_data: list[int] = []
    for o in observed_outputs:
        result_1_data.append(result_1_counts.get(o, 0))
        result_2_data.append(result_2_counts.get(o, 0))
    result_1_data = np_array(result_1_data)
    result_2_data = np_array(result_2_data)

    shapiro_result = shapiro(result_1_data)
    ks_test_result = ks_2samp(result_1_data, result_2_data)
    mw_result = mannwhitneyu(result_1_data, result_2_data)

    stat_test_results = {
        'shapiro': shapiro_result,
        'kolmogorov': ks_test_result,
        'mannwhitneyu': mw_result
    }
    print(stat_test_results)
    if shapiro_result.pvalue < .05:
        print('Not a normal distribution')
    if ks_test_result.pvalue < .05:
        print('Distributions do not match (Kolmogorov-Smirnov)')
    if mw_result.pvalue < .05:
        print('Distributions do not match (Mann-Whitney U)')

    return stat_test_results


class GroverExperiment:

    def __init__(self, experiment_id: str,
                 reference_backend: Backend,
                 scenarios: list[Scenario]):
        self._experiment_id = experiment_id
        self._reference_backend = reference_backend
        if len(scenarios) != 2: # for now, only 2 scenarios
            raise RuntimeError('Please provide exactly 2 scenarios')
        self._scenarios = scenarios

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
        runner = Runner(transpiled_circuit=self._get_transpiled_circuit())
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

    def _generate_scenario_artifacts(self, runner_result: RunnerResult):
        counts = runner_result['result'].get_counts()
        scenario = runner_result['scenario']
        file_name = f'{self._experiment_id}.{scenario._scenario_id}'
        utils.write_results_json(counts, file_name)
        utils.write_results_csv(counts, file_name)
        utils.plot(counts, file_name)
