from praline.common.pralinefile.validation.scope_validator import validate_scope
from praline.common.exception import PralinefileValidationException
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

    def test_default_scope(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0',
            'dependencies': [
                {
                    'organization': 'sugarco',
                    'artifact': 'chocolate',
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

        self.assertRaises(PralinefileValidationException, validate_scope, pralinefile)
