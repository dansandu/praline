from praline.common.constants import mandatory_fields
from praline.common.pralinefile.validation.validator import validate
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ValidatorTest(TestCase):
    def test_validator_with_full_pralinefile(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'platforms': ['darwin', 'linux'],
            'compilers': ['gcc'],
            'modes': ['debug', 'release'],
            'version': '1.2.3',
            'dependencies': [
                {
                    'organization': 'candy',
                    'artifact': 'chocolate',
                    'scope': 'test',
                    'version': '1.+0.+0'
                }
            ]
        }

        validate(pralinefile)

    def test_validator_with_short_pralinefile(self):
        pralinefile = {
            'organization': 'some_organization',
            'artifact': 'some_artifact',
            'version': '12.0.4'
        }

        validate(pralinefile)

    def test_validator_with_missing_mandatory_field(self):
        for mandatory_field in mandatory_fields:
            pralinefile = {
                'organization': 'some_organization',
                'artifact': 'some_artifact',
                'version': '12.0.4',
                'dependencies': [
                    {
                        'organization': 'candy',
                        'artifact': 'chocolate',
                        'version': '2.3.4'
                    }
                ]
            }
            pralinefile.pop(mandatory_field)

            self.assertRaises(PralinefileValidationError, validate, pralinefile)

    def test_validator_with_missing_dependency_mandatory_field(self):
        for mandatory_field in mandatory_fields:
            pralinefile = {
                'organization': 'some_organization',
                'artifact': 'some_artifact',
                'version': '12.0.4',
                'dependencies': [
                    {
                        'organization': 'candy',
                        'artifact': 'chocolate',
                        'version': '2.3.4'
                    }
                ]
            }
            pralinefile['dependencies'][0].pop(mandatory_field)

            self.assertRaises(PralinefileValidationError, validate, pralinefile)
