from unittest import TestCase, main

from mock_result import MockResult
from statistical_assertions import \
    assertIsNormalShapiro, assertSameDistributionKomogorov, \
    assertSameDistributionMannWhitneyU


class TestStatisticalAssertions(TestCase):

    def test_should_assert_not_normal_distribution(self):
        # given
        result = MockResult({
            "0000": 16,
            "0001": 15,
            "0010": 15,
            "0011": 12,
            "0100": 24,
            "0101": 18,
            "0110": 2005,
            "0111": 21,
            "1000": 11,
            "1001": 1877,
            "1010": 11,
            "1011": 14,
            "1100": 16,
            "1101": 12,
            "1110": 13,
            "1111": 16
        })

        # when & then
        with self.assertRaises(AssertionError):
            assertIsNormalShapiro(result)

    def test_should_assert_not_same_distribution_by_kolmogorov(self):
        # given
        expected_result = MockResult({
            "0000": 16,
            "0001": 15,
            "0010": 15,
            "0011": 12,
            "0100": 24,
            "0101": 18,
            "0110": 2005,
            "0111": 21,
            "1000": 11,
            "1001": 1877,
            "1010": 11,
            "1011": 14,
            "1100": 16,
            "1101": 12,
            "1110": 13,
            "1111": 16
        })

        actual_result = MockResult({
            "0000": 142,
            "0001": 177,
            "0010": 173,
            "0011": 150,
            "0100": 162,
            "0101": 120,
            "0110": 1089,
            "0111": 143,
            "1000": 143,
            "1001": 1017,
            "1010": 122,
            "1011": 143,
            "1100": 111,
            "1101": 148,
            "1110": 151,
            "1111": 105
        })

        # when & then
        with self.assertRaises(AssertionError):
            assertSameDistributionKomogorov(expected_result, actual_result)

    def test_should_assert_not_same_distribution_by_mann_whitney(self):
        # given
        expected_result = MockResult({
            "0000": 16,
            "0001": 15,
            "0010": 15,
            "0011": 12,
            "0100": 24,
            "0101": 18,
            "0110": 2005,
            "0111": 21,
            "1000": 11,
            "1001": 1877,
            "1010": 11,
            "1011": 14,
            "1100": 16,
            "1101": 12,
            "1110": 13,
            "1111": 16
        })

        actual_result = MockResult({
            "0000": 142,
            "0001": 177,
            "0010": 173,
            "0011": 150,
            "0100": 162,
            "0101": 120,
            "0110": 1089,
            "0111": 143,
            "1000": 143,
            "1001": 1017,
            "1010": 122,
            "1011": 143,
            "1100": 111,
            "1101": 148,
            "1110": 151,
            "1111": 105
        })

        # when & then
        with self.assertRaises(AssertionError):
            assertSameDistributionMannWhitneyU(expected_result, actual_result)

    def test_should_assert_same_distribution_by_kolmogorov(self):
        # given
        expected_result = MockResult({
            "0000": 4096
        })

        actual_result = MockResult({
            "0000": 4007,
            "0001": 13,
            "0010": 28,
            "0100": 30,
            "1000": 18
        })

        # when & then: does not raises exception
        assertSameDistributionKomogorov(expected_result, actual_result)


if __name__ == '__main__':
    main()
