# inheritance problem 3: BankAccount and SavingsAccount


class BankAccount:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            return False  # not enough money
        self.balance -= amount
        return True

    def transfer(self, destination, amount):
        # False if there is not enough money, True otherwise
        if not self.withdraw(amount):
            return False
        destination.deposit(amount)
        return True


class SavingsAccount(BankAccount):
    def __init__(self, account_number, balance=0, interest_rate=0.02):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate  # 0.02 = 2%

    def add_interest(self):
        self.deposit(self.balance * self.interest_rate)

    def check_balance(self):
        return self.balance


if __name__ == "__main__":
    a = BankAccount("FR001", 100)
    s = SavingsAccount("FR002", 1000, 0.05)
    print(a.transfer(s, 30))  # True
    print(a.transfer(s, 500))  # False, not enough money
    s.add_interest()
    print(a.balance, s.check_balance())  # 70 1081.5
