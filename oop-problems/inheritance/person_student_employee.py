# inheritance problem 2: Person, Student, Employee


class Person:
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address

    def introduce(self):
        return f"Hi, I'm {self.name}, I'm {self.age} and I live at {self.address}."


class Student(Person):
    def __init__(self, name, age, address, field_of_study):
        super().__init__(name, age, address)  # reuse the parent constructor
        self.field_of_study = field_of_study

    def introduce(self):
        return f"Hi, I'm {self.name}, I'm {self.age} and I study {self.field_of_study}."


class Employee(Person):
    def __init__(self, name, age, address, company):
        super().__init__(name, age, address)
        self.company = company

    def introduce(self):
        return f"Hi, I'm {self.name}, I'm {self.age} and I work at {self.company}."


if __name__ == "__main__":
    print(Person("Alice", 40, "12 rue de Paris").introduce())
    print(Student("Bob", 20, "5 rue Lille", "computer science").introduce())
    print(Employee("Chloe", 30, "8 rue Lyon", "ACME").introduce())
