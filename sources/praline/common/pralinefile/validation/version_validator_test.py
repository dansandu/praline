from praline.common.pralinefile.validation.version_validator import validate_version
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class VersionValidatorTest(TestCase):
    def test_valid_version_with_minor_wildcard(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '10.1.31',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate',
                    'version': '2.+2.+0'
                }
            ]
        }
        validate_version(pralinefile)

    def test_valid_version_with_bugfix_wildcard(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.1000.2919',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate',
                    'version': '1.1.+0'
                }
            ]
        }
        validate_version(pralinefile)

    def test_invalid_version_with_minor_wildcard(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '10.1.31',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate',
                    'version': '3.+9.111'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_version, pralinefile)

    def test_invalid_version_with_major_wildcard(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '10.1.31',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate',
                    'version': '+3.9.111'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_version, pralinefile)

    def test_invalid_version_numbers(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '0.1.31'
        }

        self.assertRaises(PralinefileValidationError, validate_version, pralinefile)

    def test_invalid_dependency_version_numbers(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '10.1.31',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate',
                    'version': '0.9.111'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_version, pralinefile)
