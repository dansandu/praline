from praline.common.pralinefile.validation.allowed_fields_validator import validate_allowed_fields
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class AllowedFieldsValidatorTest(TestCase):
    def test_valid_pralinefile(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'platforms': ['darwin', 'linux'],
            'modes': ['debug', 'release'],
            'dependencies': [
                {
                    'organization': 'candy',
                    'artifact': 'chocolate',
                    'scope': 'test',
                    'version': '1.+0.+0'
                }
            ]
        }

        validate_allowed_fields(pralinefile)

    def test_unrecognized_field(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'build': 'x32'
        }
        
        self.assertRaises(PralinefileValidationError, validate_allowed_fields, pralinefile)

    def test_unrecognized_dependency_field(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'dependencies': [
                {
                    'organization': 'candy',
                    'artifact': 'chocolate',
                    'platforms': ['darwin', 'linux']
                }
            ]
        }
        
        self.assertRaises(PralinefileValidationError, validate_allowed_fields, pralinefile)
