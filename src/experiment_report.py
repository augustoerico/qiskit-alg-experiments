from typing import TypedDict, Tuple

from qiskit.result.result import Result

from statistical_test import StatisticalTestsResultsByType

class ExperimentReport(TypedDict):
    statistical_tests_results: StatisticalTestsResultsByType
    scenarios_results: Tuple[Result, Result]
