from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_ibm_runtime.ibm_backend import Backend
from qiskit.providers import Job
from qiskit_ibm_runtime import SamplerV2 as Sampler, RuntimeJobV2 as RuntimeJob

import utils

from folders import create_artifacts_folder

from qiskit.qasm3 import dump as qasm3_dump


class Grover5qQhwExperiment:

    id: str
    reference_backend: Backend
    transpiled_circuit: QuantumCircuit

    def __init__(
        self, id: str, reference_backend: Backend):
        self.id = id
        self.reference_backend = reference_backend
        self.transpiled_circuit = self.get_transpiled_circuit()

    @utils.print_exec_time
    def get_transpiled_circuit(self) -> QuantumCircuit: # [TODO] load QASM from related exp
        boolean_expr = '(~q0 & ~q1 & ~q2 & q3 & q4) ' +\
              '| (~q0 & q1 & ~q2 & ~q3 & q4)'  # q0 top-most: least significant qubit
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

    def run(self):
        artifacts_folder_path = create_artifacts_folder(self.id)

        circuit = self.transpiled_circuit
        circuit_qasm_file_name = f'{artifacts_folder_path}/{self.id}.qasm'
        
        # [TODO] refactor into a utils function
        with open(circuit_qasm_file_name, 'w', encoding='utf-8') as file:
            qasm3_dump(circuit, file)
        
        # [TODO] load QASM from related experiment
        sampler = Sampler(self.reference_backend)
        sampler.options.default_shots = 10000
        runtime_job: RuntimeJob = sampler.run([circuit])
        # result = runtime_job.result()
        # job_file_name = f'{artifacts_folder_path}/{self.id}.job.json'
        # [FIXME] 'frozenset' object has no attribute '__dict__'. Did you mean: '__dir__'
        # with open(job_file_name, 'w', encoding='utf-8') as file:
        #     simplejson.dump(
        #         job, default=lambda o: o.__dict__,
        #         fp=file, indent=4, sort_keys=True)

        # with open(job_file_name, 'w', encoding='utf-8') as file:
        #     simplejson.dump(
        #         result, default=lambda o: o.__dict__,
        #         fp=file, indent=4, sort_keys=True)

        # Obs: results are async... have to fetch from IBM dashboard for now

def main():
    from os import environ
    from qiskit_ibm_runtime import QiskitRuntimeService

    api_token = environ.get('API_TOKEN')
    runtime_service = QiskitRuntimeService(
        channel='ibm_quantum', token=api_token
    )

    reference_backend = runtime_service.backend(name='ibm_sherbrooke')

    # [TODO] use the script name as the experiment id

    grover_experiment = Grover5qQhwExperiment(
        id='grover-5q-qhw',
        reference_backend=reference_backend)
    grover_experiment.run()


if __name__ == '__main__':
    main()