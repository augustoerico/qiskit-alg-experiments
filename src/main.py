from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider.backends import FakeTorino

from scenario import Scenario
from grover_experiment import GroverExperiment

def main():
    reference_backend = FakeTorino()

    noisy_backend = reference_backend
    ideal_backend = AerSimulator.from_backend(reference_backend)
    ideal_backend.set_options(method='statevector', noise_model=None)
    scenarios = [
        Scenario(scenario_id='noisy', backend=noisy_backend),
        Scenario(scenario_id='ideal', backend=ideal_backend)
    ]
    grover_experiment = GroverExperiment(
        experiment_id='grover2',
        reference_backend=reference_backend,
        scenarios=scenarios)
    grover_experiment.run_scenarios()

if __name__ == '__main__':
    main()
