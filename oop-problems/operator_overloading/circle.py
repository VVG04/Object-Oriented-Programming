# problem 5: Circle with the six comparison operators, compared by radius


class Circle:
    def __init__(self, radius):
        self.radius = radius

    def __lt__(self, other):
        return self.radius < other.radius

    def __gt__(self, other):
        return self.radius > other.radius

    def __eq__(self, other):
        return self.radius == other.radius

    def __ne__(self, other):
        return self.radius != other.radius

    def __ge__(self, other):
        return self.radius >= other.radius

    def __le__(self, other):
        return self.radius <= other.radius

    def __repr__(self):
        return f"Circle({self.radius})"


if __name__ == "__main__":
    small = Circle(2)
    big = Circle(5)
    print(small < big, small > big, small == big, small != big, small >= big, small <= big)
    # True False False True False True
