from praline.common.pralinefile.validation.scope_validator import validate_scope
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ScopeValidatorTest(TestCase):
    def test_valid_scope(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0',
            'dependencies': [
                {
                    'organization': 'sugarco',
                    'artifact': 'chocolate',
                    'scope': 'test',
                    'version': '1.0.0'
                }
            ]
        }
        validate_scope(pralinefile)

    def test_invalid_scope(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0',
            'dependencies': [
                {
                    'organization': 'sugarco',
                    'artifact': 'chocolate',
                    'scope': 'compile',
                    'version': '1.0.0'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_scope, pralinefile)
