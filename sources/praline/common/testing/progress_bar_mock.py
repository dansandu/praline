from unittest import TestCase


class ProgressBarMock:
    def __init__(self, test_case: TestCase, resolution: int):
        self.test_case = test_case
        self.resolution = resolution
        self.progress = 0

    def __enter__(self):
        return self
    
    def update_description(self, description: str):
        pass

    def advance(self, amount: int = 1):
        self.progress += amount
        self.test_case.assertLessEqual(self.progress, self.resolution)

    def __exit__(self, type, value, traceback):
        self.test_case.assertEqual(self.progress, self.resolution)


class ProgressBarSupplierMock:
    def __init__(self, test_case: TestCase, 
                 expected_resolution: int,
                 stage_name: str = 'stage'):
        self.test_case = test_case
        self.stage_name = stage_name
        self.expected_resolution = expected_resolution

    def create(self, resolution: int):
        self.test_case.assertEqual(resolution, self.expected_resolution)
        return ProgressBarMock(self.test_case, resolution)
