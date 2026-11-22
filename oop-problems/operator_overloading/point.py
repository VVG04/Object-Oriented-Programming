# problem 6: 2D point compared by its distance to the origin
from math import sqrt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    # we compare the distances, not the coordinates
    def __lt__(self, other):
        return self.distance() < other.distance()

    def __gt__(self, other):
        return self.distance() > other.distance()

    def __eq__(self, other):
        return self.distance() == other.distance()

    def __ne__(self, other):
        return self.distance() != other.distance()

    def __ge__(self, other):
        return self.distance() >= other.distance()

    def __le__(self, other):
        return self.distance() <= other.distance()

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


if __name__ == "__main__":
    a = Point(3, 4)  # distance 5
    b = Point(0, 5)  # distance 5
    c = Point(1, 1)  # distance 1.41...
    print(a == b)  # True: different points but same distance
    print(c < a)  # True
