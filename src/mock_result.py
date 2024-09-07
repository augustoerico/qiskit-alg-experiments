class MockResult:

    def __init__(self, counts: dict) -> None:
        self.counts = counts

    def get_counts(self):
        return self.counts
