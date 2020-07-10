from praline.common.pralinefile.validation.compilers_validator import validate_compilers
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class CompilersValidatorTest(TestCase):
    def test_valid_compilers(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'my_artifact',
            'compilers': ['gcc', 'clang', 'msvc'],
            'version': '1.5.0'
        }

        validate_compilers(pralinefile)

    def test_invalid_compilers_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'my_artifact',
            'compilers': ['gcc', 'ccg'],
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_compilers, pralinefile)

    def test_invalid_compilers_type(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'my_artifact',
            'compilers': 'gcc',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_compilers, pralinefile)

    def test_invalid_empty_compilers(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'compilers': [],
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_compilers, pralinefile)

    def test_valid_unset_compilers_field(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0'
        }
        
        validate_compilers(pralinefile)
