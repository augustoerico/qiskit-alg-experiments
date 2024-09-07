from qiskit import QuantumCircuit
from qiskit.result.result import Result

from scenario import Scenario
from utils import print_exec_time

class ScenarioRunner:

    def __init__(self, circuit: QuantumCircuit, scenario: Scenario):
        self.circuit = circuit
        self.scenario = scenario
    
    @print_exec_time
    def run(self) -> Result:
        backend = self.scenario['backend']
        shots = self.scenario.get('shots', 1024)
        
        job_result: Result = backend \
            .run(self.circuit, shots=shots) \
            .result()
        return job_result
