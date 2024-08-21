from qiskit_ibm_runtime.ibm_backend import Backend


class Scenario:

    def __init__(self, **kwargs) -> None:
        self._scenario_id: str = kwargs['scenario_id']
        self._backend: Backend = kwargs['backend']
