from typing import Tuple

from numpy import array as np_array
from qiskit.result.result import Result
from scipy.stats import shapiro, ks_2samp, mannwhitneyu

def _results_to_data_arrays(
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

def _result_to_data_array(result: Result):
    return np_array([
        v
        for _, v in sorted(
            result.get_counts().items())
        ])

def assertSameDistributionKomogorov(
    expected_result: Result, actual_result: Result,
    pvalue: float = .05):
    
    expected_data, actual_data = _results_to_data_arrays(
            expected_result, actual_result)
    
    ks_test_result = ks_2samp(expected_data, actual_data)

    if ks_test_result.pvalue < pvalue:
        message = f'Calculated p-value = {ks_test_result.pvalue} < {pvalue}\n' \
            + 'Samples derive from different distributions'
        raise AssertionError(message)

def assertSameDistributionMannWhitneyU(
    expected_result: Result, actual_result: Result,
    pvalue: float = .05):
    
    expected_data, actual_data = _results_to_data_arrays(
            expected_result, actual_result)
    
    mw_result = mannwhitneyu(expected_data, actual_data)

    if mw_result.pvalue < pvalue:
        message = f'Calculated p-value = {mw_result.pvalue} < {pvalue}\n' \
            + 'Samples derive from different distributions'
        raise AssertionError(message)


def assertIsNormalShapiro(result: Result, pvalue: float = .05):
    data = _result_to_data_array(result)
    shapiro_result = shapiro(data)

    if shapiro_result.pvalue < pvalue:
        message = f'Calculated p-value = {shapiro_result.pvalue} < {pvalue}\n' \
            + 'Samples do not derive from a normal distribution'
        raise AssertionError(message)
