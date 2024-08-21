from typing import TypedDict

from qiskit import QuantumCircuit
from qiskit.result.result import Result

from scenario import Scenario
from utils import print_exec_time

class RunnerResult(TypedDict):
    result: Result
    scenario: Scenario

class Runner:

    def __init__(self, transpiled_circuit: QuantumCircuit):
        self._transpiled_circuit = transpiled_circuit
    
    @print_exec_time
    def _run_one(self, scenario: Scenario):
        # [TODO] raise exception if it can't run a scenario for the given backend
        #   i.e. the ideal backend is too different from the real backend
        backend = scenario._backend
        
        result: Result = backend \
            .run(self._transpiled_circuit, shots=4096) \
            .result()
        
        runner_result: RunnerResult = {
            'result': result,
            'scenario': scenario
        }

        return runner_result
