import pytest

from bank_account import BankAccount, SavingsAccount
from person_student_employee import Employee, Person, Student
from vehicle import Bicycle, Car, Vehicle


def test_vehicle_drive():
    assert Vehicle().drive() == "Driving a vehicle"
    assert Car().drive() == "Driving a car"
    assert Bicycle().drive() == "Riding a bicycle"
    assert isinstance(Car(), Vehicle)


def test_person_student_employee():
    s = Student("Bob", 20, "Lille", "computer science")
    e = Employee("Chloe", 30, "Lyon", "ACME")
    assert isinstance(s, Person) and isinstance(e, Person)
    assert s.name == "Bob" and s.field_of_study == "computer science"
    assert "computer science" in s.introduce()
    assert "ACME" in e.introduce()
    assert Person("A", 1, "B").introduce() != s.introduce()


def test_deposit_and_withdraw():
    a = BankAccount("1", 100)
    a.deposit(50)
    assert a.balance == 150
    assert a.withdraw(30) is True and a.balance == 120
    assert a.withdraw(500) is False and a.balance == 120  # unchanged


def test_invalid_amounts():
    with pytest.raises(ValueError):
        BankAccount("1").deposit(-5)


def test_transfer():
    a, b = BankAccount("1", 100), BankAccount("2", 0)
    assert a.transfer(b, 40) is True
    assert (a.balance, b.balance) == (60, 40)
    assert a.transfer(b, 1000) is False
    assert (a.balance, b.balance) == (60, 40)  # nothing moved


def test_savings_account():
    s = SavingsAccount("3", 1000, 0.05)
    s.add_interest()
    assert s.check_balance() == 1050
    assert isinstance(s, BankAccount)
    # a savings account can use the transfer it inherited
    other = BankAccount("4")
    assert s.transfer(other, 50) is True
    assert other.balance == 50
