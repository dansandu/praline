from praline.common.pralinefile.validation.test_service_runner import validate_test_service_runner
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class TestServiceRunnerTest(TestCase):
    def test_valid_test_service_runner(self):
        pralinefile = {
            'organization': 'myorg',
            'artifact': 'myart',
            'version': '1.5.0',
            'test_service_runner': 'deporg-depart',
            'dependencies': [
                {
                    'organization': 'deporg',
                    'artifact': 'depart',
                    'scope': 'test',
                    'version': '1.0.0'
                }
            ]
        }
        validate_test_service_runner(pralinefile)

    def test_invalid_test_service_runners(self):
        pralinefile = {
            'organization': 'myorg',
            'artifact': 'myart',
            'version': '1.5.0',
            'test_service_runner': 'unknown',
            'dependencies': [
                {
                    'organization': 'deporg',
                    'artifact': 'depart',
                    'scope': 'test',
                    'version': '1.0.0',
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_test_service_runner, pralinefile)
