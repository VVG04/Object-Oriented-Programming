import pytest

from circle import Circle
from complex_number import ComplexNumber
from matrix import Matrix
from person import Person
from point import Point
from vector import Vector


def test_complex_add_and_sub():
    a, b = ComplexNumber(3, 4), ComplexNumber(1, -2)
    assert a + b == ComplexNumber(4, 2)
    assert a - b == ComplexNumber(2, 6)
    assert repr(a - b) == "2+6i"
    assert repr(b) == "1-2i"


def test_person_greater_by_age():
    old, young = Person("A", 30, "F"), Person("B", 25, "M")
    assert old > young
    assert not (young > old)
    assert not (old > Person("C", 30, "F"))  # same age


def test_vector_dot_product():
    assert Vector(1, 2, 3) * Vector(4, 5, 6) == 32
    assert Vector(1, 0, 0) * Vector(0, 1, 0) == 0  # perpendicular


def test_circle_all_comparisons():
    small, big = Circle(2), Circle(5)
    assert small < big and big > small
    assert small != big and not (small == big)
    assert small <= big and big >= small
    assert Circle(3) == Circle(3) and Circle(3) <= Circle(3) and Circle(3) >= Circle(3)


def test_point_compared_by_distance():
    a, b, c = Point(3, 4), Point(0, 5), Point(1, 1)
    assert a == b  # both at distance 5
    assert c < a and a > c
    assert a >= b and a <= b
    assert c != a


def test_matrix_multiplication():
    a = Matrix([[1, 2], [3, 4]])
    b = Matrix([[5, 6], [7, 8]])
    assert a * b == Matrix([[19, 22], [43, 50]])


def test_matrix_non_square():
    a = Matrix([[1, 2, 3]])  # 1x3
    b = Matrix([[1], [2], [3]])  # 3x1
    assert a * b == Matrix([[14]])
    assert b * a == Matrix([[1, 2, 3], [2, 4, 6], [3, 6, 9]])


def test_matrix_wrong_sizes():
    with pytest.raises(ValueError):
        Matrix([[1, 2]]) * Matrix([[1, 2]])
