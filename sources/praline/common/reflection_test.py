from praline.common.reflection import subclasses_of
from unittest import TestCase


class A:
    pass


class B(A):
    pass


class C(A):
    pass


class D(B):
    pass


class ReflectionTest(TestCase):
    def test_subclasses_of(self):
        classes = subclasses_of(A)

        self.assertEqual(classes, [B, C, D])
