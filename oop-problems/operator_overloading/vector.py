# problem 4: Vector in space, * gives the dot product


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other):
        # dot product: x1*x2 + y1*y2 + z1*z2 (a number, not a vector)
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"


if __name__ == "__main__":
    v1 = Vector(1, 2, 3)
    v2 = Vector(4, 5, 6)
    print(v1 * v2)  # 4 + 10 + 18 = 32
