from unittest import TestCase


class ProgressBarMock:
    def __init__(self, test_case: TestCase, resolution: int):
        self.test_case = test_case
        self.resolution = resolution
        self.progress = 0

    def __enter__(self):
        return self
    
    def update_summary(self, summary: str):
        pass

    def advance(self, amount: int = 1):
        self.progress += amount
        self.test_case.assertLessEqual(self.progress, self.resolution)

    def __exit__(self, type, value, traceback):
        self.test_case.assertEqual(self.progress, self.resolution)


class ProgressBarSupplierMock:
    def __init__(self, test_case: TestCase, expected_resolution: int, header_length: int = 10):
        self.test_case = test_case
        self.expected_resolution = expected_resolution
        self.header_length = header_length

    def create(self, resolution: int):
        self.test_case.assertEqual(resolution, self.expected_resolution)
        return ProgressBarMock(self.test_case, resolution)
