from unittest import TestCase
from piano import call_validate, CallValidator, array_of


@CallValidator.decorate
def sum(values : array_of(int)) -> int:
    res = 0
    for i in values:
        res += i

    return res


@call_validate
class TestSomething(TestCase):
    def test_something(self):
        self.assertEquals(10, sum([1, 2, 3, 4]))

    def test_fail(self):
        self.assertEquals(10, sum([1.0, 2, 3, 4]))
