from praline.common.pralinefile.validation.mandatory_fields_validator import validate_mandatory_fields
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class MandatoryFieldsValidatorTest(TestCase):
    def test_valid_pralinefile_with_dependencies(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate',
                    'version': '1.+0.+0'
                }
            ]
        }
        validate_mandatory_fields(pralinefile)

    def test_valid_pralinefile_without_dependencies(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10'
        }
        validate_mandatory_fields(pralinefile)

    def test_invalid_pralinefile_with_missing_organization(self):
        pralinefile = {
            'artifact': 'chocolaterie',
            'version': '2.3.10'
        }

        self.assertRaises(PralinefileValidationError, validate_mandatory_fields, pralinefile)

    def test_invalid_pralinefile_with_missing_dependency_organization(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'artifact': 'chocolate',
                    'version': '1.+0.+0'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_mandatory_fields, pralinefile)

    def test_invalid_pralinefile_with_missing_artifact(self):
        pralinefile = {
            'organization': 'candyco',
            'version': '2.3.10'
        }

        self.assertRaises(PralinefileValidationError, validate_mandatory_fields, pralinefile)

    def test_invalid_pralinefile_with_missing_dependency_artifact(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'version': '1.+0.+0'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_mandatory_fields, pralinefile)

    def test_invalid_pralinefile_with_missing_version(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie'
        }

        self.assertRaises(PralinefileValidationError, validate_mandatory_fields, pralinefile)

    def test_invalid_pralinefile_with_missing_dependency_version(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '2.3.10',
            'dependencies': [
                {
                    'organization': 'candyco',
                    'artifact': 'chocolate'
                }
            ]
        }

        self.assertRaises(PralinefileValidationError, validate_mandatory_fields, pralinefile)
