from typing import TypedDict

from numpy import float64, array as np_array
from qiskit.result.result import Result
from scipy.stats import shapiro, ks_2samp, mannwhitneyu


class StatisticalTestResult(TypedDict):
    statistic: float64
    pvalue: float64


class StatisticalTestsResultsByType(TypedDict):
    shapiro_wilk: StatisticalTestResult
    kolmovorog_smirnov: StatisticalTestResult
    mann_whitney_u: StatisticalTestResult


def stat_test_results(result_1: Result, result_2: Result) \
            -> StatisticalTestsResultsByType:
    result_1_counts: dict = result_1.get_counts()
    result_2_counts: dict = result_2.get_counts()
    observed_outputs = set(
        list(result_1_counts.keys()) +
        list(result_2_counts.keys())
    )

    result_1_data: list[int] = []
    result_2_data: list[int] = []
    for o in observed_outputs:
        result_1_data.append(result_1_counts.get(o, 0))
        result_2_data.append(result_2_counts.get(o, 0))
    result_1_data = np_array(result_1_data)
    result_2_data = np_array(result_2_data)

    shapiro_result = shapiro(result_1_data)
    ks_test_result = ks_2samp(result_1_data, result_2_data)
    mw_result = mannwhitneyu(result_1_data, result_2_data)

    stat_test_results = {
        "shapiro_wilk": shapiro_result,
        "kolmogorov_smirnov": ks_test_result,
        "mann_whitney_u": mw_result
    }

    return stat_test_results