from praline.common.pralinefile.validation.unique_dependencies_validator import validate_unique_dependencies
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class UniqueDependenciesValidatorTest(TestCase):
    def test_valid_dependencies(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'organization': 'sugarco',
                    'artifact': 'chocolate',
                    'version': '1.0.0'
                },
                {
                    'organization': 'jellyco',
                    'artifact': 'popsicle',
                    'version': '2.1.0'
                },
            ]
        }
        validate_unique_dependencies(pralinefile)

    def test_invalid_self_reference_dependency(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'organization': 'sugarco',
                    'artifact': 'chocolate',
                    'version': '1.0.0'
                },
                {
                    'organization': 'candyco',
                    'artifact': 'chocolaterie',
                    'version': '2.1.0'
                },
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_unique_dependencies, pralinefile)

    def test_invalid_duplicate_dependencies(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'organization': 'sugarco',
                    'artifact': 'icecream',
                    'version': '1.0.0'
                },
                {
                    'organization': 'sugarco',
                    'artifact': 'icecream',
                    'version': '1.2.2'
                },
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_unique_dependencies, pralinefile)
