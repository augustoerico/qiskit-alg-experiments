from qiskit import QuantumCircuit
from qiskit.result.result import Result
from qiskit_ibm_runtime.ibm_backend import Backend

import utils


@utils.print_exec_time
def run_experiment(
        experiment_id: str,
        backend: Backend,
        transpiled_circuit: QuantumCircuit):

    result: Result = backend \
        .run(transpiled_circuit, shots=4096) \
        .result()

    utils.plot(result.get_counts(), experiment_id)
    utils.write_results_json(result.get_counts(), experiment_id)
    utils.write_results_csv(result.get_counts(), experiment_id)

    return result
