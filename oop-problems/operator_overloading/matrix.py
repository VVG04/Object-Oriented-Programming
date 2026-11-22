# problem 7: matrix multiplication with *


class Matrix:
    def __init__(self, rows):
        self.rows = rows

    def __mul__(self, other):
        # we can only multiply if columns of the first = rows of the second
        if len(self.rows[0]) != len(other.rows):
            raise ValueError("cannot multiply: columns of the first matrix must equal rows of the second")
        result = []
        for row in self.rows:
            new_row = []
            for col in range(len(other.rows[0])):
                # line i of A times column j of B
                total = 0
                for k in range(len(row)):
                    total += row[k] * other.rows[k][col]
                new_row.append(total)
            result.append(new_row)
        return Matrix(result)

    def __eq__(self, other):
        return self.rows == other.rows

    def __repr__(self):
        return f"Matrix({self.rows})"


if __name__ == "__main__":
    a = Matrix([[1, 2], [3, 4]])
    b = Matrix([[5, 6], [7, 8]])
    print(a * b)  # Matrix([[19, 22], [43, 50]])
