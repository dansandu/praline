from praline.common.pralinefile.validation.organization_validator import validate_organization
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class OrganizationValidatorTest(TestCase):
    def test_valid_organization(self):
        pralinefile = {
            'organization': 'my_organization'
        }
        
        validate_organization(pralinefile)

    def test_invalid_organization_with_prefix(self):
        pralinefile = {
            'organization': '_my_organization'
        }
        
        self.assertRaises(PralinefileValidationError, validate_organization, pralinefile)

    def test_invalid_organization_with_sufix(self):
        pralinefile = {
            'organization': 'my_organization_'
        }
        
        self.assertRaises(PralinefileValidationError, validate_organization, pralinefile)

    def test_invalid_organization_with_numbers(self):
        pralinefile = {
            'organization': '23my_organization'
        }
        
        self.assertRaises(PralinefileValidationError, validate_organization, pralinefile)
