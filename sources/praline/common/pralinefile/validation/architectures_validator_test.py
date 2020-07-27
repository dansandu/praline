from praline.common.pralinefile.validation.architectures_validator import validate_architecture
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ArchitecturesValidatorTest(TestCase):
    def test_valid_architectures(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'architectures': ['arm', 'x32', 'x64'],
            'version': '1.5.0'
        }
        validate_architecture(pralinefile)

    def test_invalid_architecture_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'architectures': ['potato'],
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_architecture, pralinefile)

    def test_invalid_architecture_type(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'architectures': 'arm',
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_architecture, pralinefile)

    def test_invalid_empty_architectures(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'architectures': [],
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_architecture, pralinefile)

    def test_valid_unset_architectures_field(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0'
        }
        
        validate_architecture(pralinefile)
