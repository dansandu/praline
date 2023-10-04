from praline.client.project.pipeline.stage_resources import (StageResources, ResourceNotPresentError, 
                                                             ResourceOverriddenError, UndeclaredResourceSuppliedError,
                                                             DeclaredResourceNotSuppliedError)

from unittest import TestCase


class StageResourcesTest(TestCase):
    def test_empty_resources(self):
        with StageResources('compile', 0, {}, ['objects']) as resources:
            self.assertFalse('objects' in resources)
            self.assertRaises(ResourceNotPresentError, resources.__getitem__, 'objects')

            expected_objects = 'myObjects'
            resources['objects'] = expected_objects

            self.assertIn('objects', resources)
            self.assertEqual(resources['objects'], expected_objects)
            self.assertRaises(UndeclaredResourceSuppliedError, resources.__setitem__, 'sources', 'mySources')

    def test_populated_resources(self):
        with StageResources('test', 0, {'package': 'myPackage'}, ['tests_passed']) as resources:
            self.assertIn('package', resources)
            self.assertNotIn('tests_passed', resources)
            self.assertEqual(resources['package'], 'myPackage')
            
            expected_tests_passed = 'OK'
            resources['tests_passed'] = expected_tests_passed

            self.assertIn('package', resources)
            self.assertIn('tests_passed', resources)
            self.assertEqual(resources['package'], 'myPackage')
            self.assertEqual(resources['tests_passed'], expected_tests_passed)
            self.assertRaises(ResourceOverriddenError, resources.__setitem__, 'package', 'anotherPackage')

    def test_unsupplied_resource(self):
        try:
            with StageResources('format', 0, {'source': 'mySource'}, ['formatted_source']):
                pass
        except DeclaredResourceNotSuppliedError:
            pass
