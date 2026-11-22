# exercise 3 (slide 67): oop problems

Run any file with python, for example `python3 operator_overloading/vector.py`, or run the tests:

```bash
cd oop-problems
pip install pytest
pytest
```

## operator overloading

Special methods (the ones with double underscores) let our own classes work with `+`, `-`, `*`, `>`, `==`... For example `a + b` calls `a.__add__(b)`.

| problem | file | what it does | special methods |
| --- | --- | --- | --- |
| 1 | `complex_number.py` | adds and subtracts complex numbers | `__add__`, `__sub__` |
| 2 | `person.py` | `p1 > p2` is True if p1 is older | `__gt__` |
| 4 | `vector.py` | `v1 * v2` is the dot product (a number) | `__mul__` |
| 5 | `circle.py` | the 6 comparisons, by radius | `__lt__`, `__gt__`, `__eq__`, `__ne__`, `__ge__`, `__le__` |
| 6 | `point.py` | the 6 comparisons, by distance to origin `sqrt(x² + y²)` | same six |
| 7 | `matrix.py` | matrix multiplication | `__mul__` |

(The statement has no problem 3.)

Things to remember:
- `__repr__` is what `print` shows for the object, `__eq__` is what `==` calls.
- For the dot product, `*` returns a **number**; for matrices it returns a **new Matrix**. The operator is just a method, so we choose what it returns.
- Matrix product: the number of columns of the first matrix must equal the number of rows of the second, and `result[i][j]` = line `i` of A times column `j` of B.
- In `point.py`, two different points can be "equal" (`Point(3, 4) == Point(0, 5)`) because we compare distances.

## inheritance

| problem | file | idea |
| --- | --- | --- |
| 1 | `vehicle.py` | `Car` and `Bicycle` **override** `drive()` of `Vehicle` (polymorphism) |
| 2 | `person_student_employee.py` | `Student` and `Employee` extend `Person`, call `super().__init__(...)` and have their own `introduce()` |
| 3 | `bank_account.py` | `SavingsAccount` extends `BankAccount` and adds `interest_rate`, `add_interest()`, `check_balance()`; `transfer` is inherited |

Things to remember:
- `class Car(Vehicle)` means "a Car is a Vehicle" (an is-a relation).
- `super().__init__(...)` runs the parent's constructor so we don't copy its code.
- A child can use everything the parent has, which is why `SavingsAccount` can call `transfer` without redefining it.
