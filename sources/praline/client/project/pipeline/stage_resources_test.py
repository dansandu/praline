from praline.client.project.pipeline.stage_resources import StageResources, ResourceNotPresentError, ResourceOverriddenError, UndeclaredResourceSuppliedError
from unittest import TestCase


class StageResourcesTest(TestCase):
    def test_empty_resources(self):
        resources = StageResources('compile', 0, {}, ['objects'])

        self.assertFalse('objects' in resources)
        self.assertRaises(ResourceNotPresentError, resources.__getitem__, 'objects')

        expected_objects = 'myObjects'
        resources['objects'] = expected_objects

        self.assertIn('objects', resources)
        self.assertEqual(resources['objects'], expected_objects)
        self.assertRaises(UndeclaredResourceSuppliedError, resources.__setitem__, 'sources', 'mySources')

    def test_populated_resources(self):
        resources = StageResources('test', 0, {'package': 'myPackage'}, ['test_results'])

        self.assertIn('package', resources)
        self.assertNotIn('test_results', resources)
        self.assertEqual(resources['package'], 'myPackage')
        
        expected_test_results = 'OK'
        resources['test_results'] = expected_test_results

        self.assertIn('package', resources)
        self.assertIn('test_results', resources)
        self.assertEqual(resources['package'], 'myPackage')
        self.assertEqual(resources['test_results'], expected_test_results)
        self.assertRaises(ResourceOverriddenError, resources.__setitem__, 'package', 'anotherPackage')
