from praline.common.pralinefile.validation.test_service_validator import validate_test_service
from praline.common.exception import PralinefileValidationException

from unittest import TestCase


class TestServiceTest(TestCase):
    def test_valid_test_service(self):
        pralinefile = {
            'organization': 'myorg',
            'artifact': 'myart',
            'version': '1.5.0',
            'test_service': {
                'executable_to_run': 'exeorg-exeart',
                'library_to_load': 'liborg-libart',
                'service_name': 'some-service',
            },
            'dependencies': [
                {
                    'organization': 'exeorg',
                    'artifact': 'exeart',
                    'scope': 'test',
                    'version': '1.0.0'
                },
                {
                    'organization': 'liborg',
                    'artifact': 'libart',
                    'scope': 'test',
                    'version': '1.0.0'
                }
            ]
        }
        validate_test_service(pralinefile)

    def test_invalid_test_service(self):
        pralinefile = {
            'organization': 'myorg',
            'artifact': 'myart',
            'version': '1.5.0',
            'test_service': 'unknown',
            'dependencies': [
                {
                    'organization': 'deporg',
                    'artifact': 'depart',
                    'scope': 'test',
                    'version': '1.0.0',
                }
            ]
        }

        self.assertRaises(PralinefileValidationException, validate_test_service, pralinefile)
