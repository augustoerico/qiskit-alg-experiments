from typing import TypedDict

from qiskit_ibm_runtime.ibm_backend import Backend


class Scenario(TypedDict):
    id: str
    backend: Backend
    shots: int
