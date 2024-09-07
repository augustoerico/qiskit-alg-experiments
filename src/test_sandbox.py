from unittest import TestCase, TestSuite, main, TextTestRunner


def create_test_suite(numbers_mason: list[int]):
    suite = TestSuite()
    for n in numbers_mason:
        test_case = TestSandbox(number_mason=n)
        suite.addTest(test_case)
    return suite

class ExperimentTestRunner(TextTestRunner):

    def run(self, test):
        print('aehooo')
        result = super().run(test)
        print('eooooo')
        return result


class TestSandbox(TestCase):

    @classmethod
    def setUpClass(cls):
        self.number_mason = 5

    def test_should_do_something(self):
        assert self.number_mason + 1 == 6
    
    def test_should_do_another_thing(self):
        assert 'a' + f'{self.number_mason}' == 'a5'


if __name__ == '__main__':
    numbers_mason = [5]
    suite = create_test_suite(numbers_mason)
    runner = ExperimentTestRunner()
    runner.run(suite)
