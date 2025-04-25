from praline.common.pralinefile.validation.test_service_name import validate_test_service_name
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class TestServiceNameTest(TestCase):
    def test_valid_test_service_name(self):
        pralinefile = {
            'organization': 'myorg',
            'artifact': 'myart',
            'version': '1.5.0',
            'test_service_name': 'custom_runner',
            'dependencies': [
                {
                    'organization': 'deporg',
                    'artifact': 'depart',
                    'scope': 'test',
                    'version': '1.0.0'
                }
            ]
        }
        validate_test_service_name(pralinefile)

    def test_invalid_test_service_runners(self):
        pralinefile = {
            'organization': 'myorg',
            'artifact': 'myart',
            'version': '1.5.0',
            'test_service_name': 123,
            'dependencies': [
                {
                    'organization': 'deporg',
                    'artifact': 'depart',
                    'scope': 'test',
                    'version': '1.0.0',
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_test_service_name, pralinefile)
