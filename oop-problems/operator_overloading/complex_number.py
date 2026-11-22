# problem 1: complex numbers with + and -


class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        # (a + bi) + (c + di) = (a + c) + (b + d)i
        return ComplexNumber(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return ComplexNumber(self.real - other.real, self.imag - other.imag)

    def __eq__(self, other):
        return self.real == other.real and self.imag == other.imag

    def __repr__(self):
        sign = "+" if self.imag >= 0 else "-"
        return f"{self.real}{sign}{abs(self.imag)}i"


if __name__ == "__main__":
    a = ComplexNumber(3, 4)
    b = ComplexNumber(1, -2)
    print(a + b)  # 4+2i
    print(a - b)  # 2+6i
