"""Factory Method pattern: refactor a payment system.

Before: one process_payment() with an if/elif branch per payment type.
After : one class per payment type + a factory that picks the right class.

Adding Apple Pay now = write ONE new class and register it. Nothing that already
works is touched (Open/Closed Principle: open for extension, closed for modification).
"""

from abc import ABC, abstractmethod


# 1. The interface (the blueprint) ------------------------------------------
class PaymentProcessor(ABC):
    """Every processor PROMISES to have these two methods.

    Because they are @abstractmethod, Python refuses to create a subclass
    object that forgets one of them (TypeError at instantiation).
    """

    method_name = "abstract"

    @abstractmethod
    def validation_error(self, details: dict) -> str | None:
        """Return an error message if the details are invalid, else None."""

    @abstractmethod
    def calculate_fee(self, amount: float) -> float:
        """Return the fee charged for this payment method."""

    # Concrete methods in the ABC: written ONCE, shared by every subclass.
    def validate(self, details: dict) -> bool:
        return self.validation_error(details) is None

    def process(self, amount: float, details: dict) -> dict:
        """The common workflow: validate, compute the fee, build the result."""
        error = self.validation_error(details)
        if error:
            return {"success": False, "error": error}
        fee = round(self.calculate_fee(amount), 2)
        return {
            "success": True,
            "method": self.method_name,
            "amount": round(amount + fee, 2),
            "fee": fee,
        }


# 2. Concrete implementations -----------------------------------------------
class CreditCardProcessor(PaymentProcessor):
    method_name = "credit_card"

    def validation_error(self, details: dict) -> str | None:
        if len(details.get("card_number") or "") != 16:
            return "Invalid card number"
        if len(details.get("cvv") or "") != 3:
            return "Invalid CVV"
        return None

    def calculate_fee(self, amount: float) -> float:
        return amount * 0.029  # 2.9%


class BankTransferProcessor(PaymentProcessor):
    method_name = "bank_transfer"

    def validation_error(self, details: dict) -> str | None:
        if len(details.get("iban") or "") < 15:
            return "Invalid IBAN"
        return None

    def calculate_fee(self, amount: float) -> float:
        return 1.50  # flat fee


class PayPalProcessor(PaymentProcessor):
    method_name = "paypal"

    def validation_error(self, details: dict) -> str | None:
        if "@" not in (details.get("email") or ""):
            return "Invalid PayPal email"
        return None

    def calculate_fee(self, amount: float) -> float:
        return amount * 0.034 + 0.30  # 3.4% + 0.30 EUR


# 3. The factory --------------------------------------------------------------
class PaymentFactory:
    """The "middleman": give it a string, get back the right processor.

    A dictionary maps names to classes, so there is no if/elif chain at all.
    """

    _processors: dict[str, type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "bank_transfer": BankTransferProcessor,
        "paypal": PayPalProcessor,
    }

    @classmethod
    def register(cls, name: str, processor_class: type[PaymentProcessor]) -> None:
        """Add a new payment method WITHOUT editing this file (e.g. Apple Pay)."""
        cls._processors[name] = processor_class

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        try:
            processor_class = self._processors[payment_type]
        except KeyError:
            raise ValueError(f"Unknown payment type: {payment_type}") from None
        return processor_class()  # the factory creates the object


if __name__ == "__main__":
    factory = PaymentFactory()

    processor = factory.get_processor("credit_card")
    print(processor.process(100.0, {"card_number": "1234567890123456", "cvv": "123"}))

    processor = factory.get_processor("bank_transfer")
    print(processor.process(100.0, {"iban": "FR7630006000011234567890189", "bic": "BNPAFRPP"}))

    processor = factory.get_processor("paypal")
    print(processor.process(100.0, {"email": "victor@example.com"}))

    # Extending the system: a new class + one register() call. No old code edited.
    class ApplePayProcessor(PaymentProcessor):
        method_name = "apple_pay"

        def validation_error(self, details: dict) -> str | None:
            return None if details.get("device_token") else "Missing Apple Pay device token"

        def calculate_fee(self, amount: float) -> float:
            return amount * 0.015

    PaymentFactory.register("apple_pay", ApplePayProcessor)
    print(factory.get_processor("apple_pay").process(100.0, {"device_token": "abc"}))
