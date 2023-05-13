from praline.common import ArtifactVersion, DependencyVersion, PackageVersion

from datetime import datetime, timezone
from unittest import TestCase


class PralineCommonTest(TestCase):
    def test_artifact_version(self):
        version_string = '1.2.3'

        version = ArtifactVersion.from_string(version_string)

        self.assertEqual(version.major, 1)

        self.assertEqual(version.minor, 2)

        self.assertEqual(version.patch, 3)

        self.assertFalse(version.snapshot)

        self.assertEqual(str(version), version_string)

    def test_artifact_version_snapshot(self):
        version_string = '4.5.6.SNAPSHOT'

        version = ArtifactVersion.from_string(version_string)

        self.assertEqual(version.major, 4)

        self.assertEqual(version.minor, 5)

        self.assertEqual(version.patch, 6)

        self.assertTrue(version.snapshot)

        self.assertEqual(str(version), version_string)

    def test_dependency_version_minor_wildcard(self):
        version = DependencyVersion.from_string('0.+1.0')

        self.assertEqual(version.major, 0)

        self.assertEqual(version.minor, 1)

        self.assertEqual(version.patch, 0)

        self.assertFalse(version.snapshot)

        self.assertTrue(version.minor_wildcard)

        self.assertTrue(version.patch_wildcard)

        self.assertEqual(str(version), '0.+1.+0')

    def test_dependency_version_patch_wildcard(self):
        version_string = '0.0.+0'

        version = DependencyVersion.from_string(version_string)

        self.assertEqual(version.major, 0)

        self.assertEqual(version.minor, 0)

        self.assertEqual(version.patch, 0)

        self.assertFalse(version.snapshot)

        self.assertFalse(version.minor_wildcard)

        self.assertTrue(version.patch_wildcard)

        self.assertEqual(str(version), version_string)

    def test_dependency_version_wildcard_snapshot(self):
        version_string = '2.+5.+11.SNAPSHOT'

        version = DependencyVersion.from_string(version_string)

        self.assertEqual(version.major, 2)

        self.assertEqual(version.minor, 5)

        self.assertEqual(version.patch, 11)

        self.assertTrue(version.snapshot)

        self.assertTrue(version.minor_wildcard)

        self.assertTrue(version.patch_wildcard)

        self.assertEqual(str(version), version_string)

    def test_package_version(self):
        version_string = '3.1.5'

        version = PackageVersion.from_string(version_string)

        self.assertEqual(version.major, 3)

        self.assertEqual(version.minor, 1)

        self.assertEqual(version.patch, 5)

        self.assertFalse(version.snapshot)

        self.assertIsNone(version.timestamp)

        self.assertEqual(str(version), version_string)

    def test_package_version_snapshot(self):
        version_string = '22.6.8.SNAPSHOT20090102030405000006'

        version = PackageVersion.from_string(version_string)

        self.assertEqual(version.major, 22)

        self.assertEqual(version.minor, 6)

        self.assertEqual(version.patch, 8)

        self.assertTrue(version.snapshot)

        expected_timestamp = datetime(year=2009, 
                                      month=1, 
                                      day=2, 
                                      hour=3, 
                                      minute=4, 
                                      second=5, 
                                      microsecond=6,
                                      tzinfo=timezone.utc)

        self.assertEqual(version.timestamp, expected_timestamp)

        self.assertEqual(str(version), version_string)

    def test_package_version_matching(self):
        version = DependencyVersion.from_string('1.2.3')

        matches = [
            PackageVersion.from_string('1.2.3'),
        ]

        mismatches = [
            PackageVersion.from_string('2.2.3'),
            PackageVersion.from_string('2.2.3.SNAPSHOT20010203040506000009'),
            PackageVersion.from_string('1.3.4'),
            PackageVersion.from_string('1.3.4.SNAPSHOT20010203040506000008'),
            PackageVersion.from_string('1.3.3'),
            PackageVersion.from_string('1.3.3.SNAPSHOT20010203040506000007'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000006'),
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000005'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506000004'),
            PackageVersion.from_string('1.2.2'),
            PackageVersion.from_string('1.2.2.SNAPSHOT20010203040506000003'),
            PackageVersion.from_string('1.1.3'),
            PackageVersion.from_string('1.1.3.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.1.2'),
            PackageVersion.from_string('1.1.2.SNAPSHOT20010203040506000001'),
        ]

        for match in matches:
            self.assertTrue(version.matches(match), f"{version} should match {match}")
        
        for mismatch in mismatches:
            self.assertFalse(version.matches(mismatch), f"{version} should not match {mismatch}")

    def test_package_version_matching_patch_wildcard(self):
        version = DependencyVersion.from_string('1.2.+3')

        matches = [
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.2.3'),
        ]

        mismatches = [
            PackageVersion.from_string('2.2.3'),
            PackageVersion.from_string('2.2.3.SNAPSHOT20010203040506000009'),
            PackageVersion.from_string('1.3.4'),
            PackageVersion.from_string('1.3.4.SNAPSHOT20010203040506000008'),
            PackageVersion.from_string('1.3.3'),
            PackageVersion.from_string('1.3.3.SNAPSHOT20010203040506000007'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000006'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000005'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506000004'),
            PackageVersion.from_string('1.2.2'),
            PackageVersion.from_string('1.2.2.SNAPSHOT20010203040506000003'),
            PackageVersion.from_string('1.1.3'),
            PackageVersion.from_string('1.1.3.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.1.2'),
            PackageVersion.from_string('1.1.2.SNAPSHOT20010203040506000001'),
        ]

        for match in matches:
            self.assertTrue(version.matches(match), f"{version} should match {match}")
        
        for mismatch in mismatches:
            self.assertFalse(version.matches(mismatch), f"{version} should not match {mismatch}")

    def test_package_version_matching_minor_wildcard(self):
        version = DependencyVersion.from_string('1.+2.+3')

        matches = [
            PackageVersion.from_string('1.3.4'),
            PackageVersion.from_string('1.3.3'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.2.3'),
        ]

        mismatches = [
            PackageVersion.from_string('2.2.3'),
            PackageVersion.from_string('2.2.3.SNAPSHOT20010203040506000009'),
            PackageVersion.from_string('1.3.4.SNAPSHOT20010203040506000008'),
            PackageVersion.from_string('1.3.3.SNAPSHOT20010203040506000007'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000006'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000005'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506000004'),
            PackageVersion.from_string('1.2.2'),
            PackageVersion.from_string('1.2.2.SNAPSHOT20010203040506000003'),
            PackageVersion.from_string('1.1.3'),
            PackageVersion.from_string('1.1.3.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.1.2'),
            PackageVersion.from_string('1.1.2.SNAPSHOT20010203040506000001'),
        ]

        for match in matches:
            self.assertTrue(version.matches(match), f"{version} should match {match}")
        
        for mismatch in mismatches:
            self.assertFalse(version.matches(mismatch), f"{version} should not match {mismatch}")

    def test_package_version_matching_snapshot(self):
        version = DependencyVersion.from_string('1.2.3.SNAPSHOT')

        matches = [
            PackageVersion.from_string('1.2.3'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506000010'),
        ]

        mismatches = [
            PackageVersion.from_string('2.2.3'),
            PackageVersion.from_string('2.2.3.SNAPSHOT20010203040506000009'),
            PackageVersion.from_string('1.3.4'),
            PackageVersion.from_string('1.3.4.SNAPSHOT20010203040506000008'),
            PackageVersion.from_string('1.3.3'),
            PackageVersion.from_string('1.3.3.SNAPSHOT20010203040506000007'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000006'),
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000005'),
            PackageVersion.from_string('1.2.2'),
            PackageVersion.from_string('1.2.2.SNAPSHOT20010203040506000003'),
            PackageVersion.from_string('1.1.3'),
            PackageVersion.from_string('1.1.3.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.1.2'),
            PackageVersion.from_string('1.1.2.SNAPSHOT20010203040506000001'),
        ]

        for match in matches:
            self.assertTrue(version.matches(match), f"{version} should match {match}")
        
        for mismatch in mismatches:
            self.assertFalse(version.matches(mismatch), f"{version} should not match {mismatch}")

    def test_package_version_matching_patch_wildcard_snapshot(self):
        version = DependencyVersion.from_string('1.2.+3.SNAPSHOT')

        matches = [
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000009'),
            PackageVersion.from_string('1.2.3'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506000008'),
        ]

        mismatches = [
            PackageVersion.from_string('2.2.3'),
            PackageVersion.from_string('2.2.3.SNAPSHOT20010203040506000007'),
            PackageVersion.from_string('1.3.4'),
            PackageVersion.from_string('1.3.4.SNAPSHOT20010203040506000006'),
            PackageVersion.from_string('1.3.3'),
            PackageVersion.from_string('1.3.3.SNAPSHOT20010203040506000005'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000004'),
            PackageVersion.from_string('1.2.2'),
            PackageVersion.from_string('1.2.2.SNAPSHOT20010203040506000003'),
            PackageVersion.from_string('1.1.3'),
            PackageVersion.from_string('1.1.3.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.1.2'),
            PackageVersion.from_string('1.1.2.SNAPSHOT20010203040506000001'),
        ]

        for match in matches:
            self.assertTrue(version.matches(match), f"{version} should match {match}")
        
        for mismatch in mismatches:
            self.assertFalse(version.matches(mismatch), f"{version} should not match {mismatch}")

    def test_package_version_matching_minor_wildcard_snapshot(self):
        version = DependencyVersion.from_string('1.+2.+3.SNAPSHOT')

        matches = [
            PackageVersion.from_string('1.3.4'),
            PackageVersion.from_string('1.3.4.SNAPSHOT20010203040506000008'),
            PackageVersion.from_string('1.3.3'),
            PackageVersion.from_string('1.3.3.SNAPSHOT20010203040506000007'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000006'),
            PackageVersion.from_string('1.2.3'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506000005'),
        ]

        mismatches = [
            PackageVersion.from_string('2.2.3'),
            PackageVersion.from_string('2.2.3.SNAPSHOT20010203040506000004'),
            PackageVersion.from_string('1.2.2'),
            PackageVersion.from_string('1.2.2.SNAPSHOT20010203040506000003'),
            PackageVersion.from_string('1.1.3'),
            PackageVersion.from_string('1.1.3.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.1.2'),
            PackageVersion.from_string('1.1.2.SNAPSHOT20010203040506000001'),
        ]

        for match in matches:
            self.assertTrue(version.matches(match), f"{version} should match {match}")
        
        for mismatch in mismatches:
            self.assertFalse(version.matches(mismatch), f"{version} should not match {mismatch}")

    def test_dependency_version_ordering(self):
        versions = [
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506002000'),
            PackageVersion.from_string('2.2.0'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000020'),
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000200'),
            PackageVersion.from_string('2.2.0.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000100'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000010'),
            PackageVersion.from_string('1.2.3'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506001000'),
            PackageVersion.from_string('2.2.0.SNAPSHOT20010203040506000001'),
        ]

        expected_sorted_versions = [
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506001000'),
            PackageVersion.from_string('1.2.3.SNAPSHOT20010203040506002000'),
            PackageVersion.from_string('1.2.3'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000100'),
            PackageVersion.from_string('1.2.4.SNAPSHOT20010203040506000200'),
            PackageVersion.from_string('1.2.4'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000010'),
            PackageVersion.from_string('1.3.0.SNAPSHOT20010203040506000020'),
            PackageVersion.from_string('1.3.0'),
            PackageVersion.from_string('2.2.0.SNAPSHOT20010203040506000001'),
            PackageVersion.from_string('2.2.0.SNAPSHOT20010203040506000002'),
            PackageVersion.from_string('2.2.0'),
        ]

        sorted_versions = sorted(versions)

        self.assertEqual(sorted_versions, expected_sorted_versions)
