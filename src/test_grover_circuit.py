from unittest import TestCase, TestResult, TestSuite

from parameterized import parameterized
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit.result.result import Result
from qiskit_aer import AerSimulator
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_ibm_runtime.ibm_backend import Backend

from mock_result import MockResult
from statistical_assertions import \
    assertSameDistributionKomogorov



def get_circuit(backend: Backend):
    boolean_expr = 'x & y' 
    oracle: QuantumCircuit = PhaseOracle(boolean_expr)
    problem = AmplificationProblem(oracle)

    num_known_solutions = 1
    optimal_num_iterations = Grover.optimal_num_iterations(
        num_solutions=num_known_solutions,
        num_qubits=oracle.num_qubits)
    
    circuit = Grover(iterations=optimal_num_iterations) \
        .construct_circuit(problem, measurement=True)

    transpiled_circuit = transpile(
        circuit, backend=backend, optimization_level=3)
    return transpiled_circuit


class TestGroverCircuit(TestCase):

    def __init__(
            self, circuit: QuantumCircuit, backend: Backend,
            expected_result: MockResult, shots: int = 1024):
        super().__init__()
        self.circuit = circuit
        self.backend = backend
        self.shots = shots
        self.expected_result = expected_result

    @classmethod
    def get_circuit(backend: Backend):
        boolean_expr = 'x & y' 
        oracle: QuantumCircuit = PhaseOracle(boolean_expr)
        problem = AmplificationProblem(oracle)

        num_known_solutions = 1
        optimal_num_iterations = Grover.optimal_num_iterations(
            num_solutions=num_known_solutions,
            num_qubits=oracle.num_qubits)
        
        circuit = Grover(iterations=optimal_num_iterations) \
            .construct_circuit(problem, measurement=True)

        transpiled_circuit = transpile(
            circuit, backend=backend, optimization_level=3)
        return transpiled_circuit

    @classmethod
    def get_expected_result():
        return MockResult({
            "0000": 7,
            "0001": 7,
            "0010": 7,
            "0011": 7,
            "0100": 7,
            "0101": 7,
            "0110": 1999,
            "0111": 7,
            "1000": 7,
            "1001": 1999,
            "1010": 7,
            "1011": 7,
            "1100": 7,
            "1101": 7,
            "1110": 7,
            "1111": 7
        })

    def test_circuit_should_return_the_expected_distribution(self):
        # given
        backend = self.backend
        circuit = self.circuit
        shots = self.shots

        # when
        actual_result: Result = backend \
            .run(circuit, shots=shots) \
            .result()

        # then
        assertSameDistributionKomogorov(
            self.expected_result, actual_result)


if __name__ == '__main__':
    backend = AerSimulator()
    circuit = get_circuit(backend)
    expected_result = MockResult({
        "0000": 7,
        "0001": 7,
        "0010": 7,
        "0011": 7,
        "0100": 7,
        "0101": 7,
        "0110": 1999,
        "0111": 7,
        "1000": 7,
        "1001": 1999,
        "1010": 7,
        "1011": 7,
        "1100": 7,
        "1101": 7,
        "1110": 7,
        "1111": 7
    })
    shots = 4096

    test_case = TestGroverCircuit(
        circuit=circuit, backend=backend,
        expected_result=expected_result, shots=shots)
    test_result = TestResult()
    test_case.run(test_result)
