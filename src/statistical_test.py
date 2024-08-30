from typing import TypedDict, Tuple

from numpy import float64, array as np_array
from qiskit.result.result import Result
from scipy.stats import chi2_contingency


class StatisticalTestResult(TypedDict):
    statistic: float64
    pvalue: float64


class StatisticalTestsResultsByType(TypedDict):
    chi2_contingency: StatisticalTestResult


def results_to_data_arrays(
    expected_result: Result, actual_result: Result) -> Tuple:
    expected_counts: dict = expected_result.get_counts()
    actual_counts: dict = actual_result.get_counts()
    observed_outputs = set(
        list(expected_counts.keys()) +
        list(actual_counts.keys())
    )

    expected_data: list[int] = []
    actual_data: list[int] = []
    for o in observed_outputs:
        expected_data.append(expected_counts.get(o, 0))
        actual_data.append(actual_counts.get(o, 0))
    expected_data = np_array(expected_data)
    actual_data = np_array(actual_data)

    return expected_data, actual_data


def stat_test_results(expected_result: Result, actual_result: Result) \
            -> StatisticalTestsResultsByType:
    expected_data, actual_data = results_to_data_arrays(
            expected_result, actual_result)
    
    chi2_test_result = chi2_contingency([expected_data, actual_data])
    stat_test_results = {
        "chi2_contingency": chi2_test_result,
    }

    return stat_test_results