"""Decorator pattern: order pricing options.

Before: calculate_total() with 5 boolean flags and one big method.
After : a BaseOrder wrapped in as many option "layers" as we want. Each layer adds
its own cost and description, then delegates to the order it wraps.

Note: this is the DESIGN pattern "Decorator" (wrapping objects). It is related to,
but not the same thing as, Python's @decorator syntax (wrapping functions).
"""

from abc import ABC, abstractmethod


# The component interface -----------------------------------------------------
class OrderComponent(ABC):
    @abstractmethod
    def get_cost(self) -> float: ...

    @abstractmethod
    def get_description(self) -> str: ...


# The concrete component ----------------------------------------------------------
class BaseOrder(OrderComponent):
    def __init__(self, base_price: float):
        self.base_price = base_price

    def get_cost(self) -> float:
        return self.base_price

    def get_description(self) -> str:
        return f"Base price: {self.base_price:.2f}€"


# The base decorator: IS an OrderComponent and HAS an OrderComponent --------------
class OrderDecorator(OrderComponent):
    def __init__(self, order: OrderComponent):
        self._order = order  # protected, by convention (slide 87)

    # Default behaviour = pass everything through to the wrapped order.
    def get_cost(self) -> float:
        return self._order.get_cost()

    def get_description(self) -> str:
        return self._order.get_description()


# Concrete decorators: each one only knows its own rule ----------------------------
class ExpressShippingDecorator(OrderDecorator):
    COST = 15.00

    def get_cost(self) -> float:
        return self._order.get_cost() + self.COST

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nExpress shipping: +{self.COST:.2f}€"


class InsuranceDecorator(OrderDecorator):
    RATE = 0.05

    def _insurance(self) -> float:
        # 5% of the cost of what it wraps (the original code used 5% of base price;
        # wrapping the BaseOrder directly gives exactly that).
        return self._order.get_cost() * self.RATE

    def get_cost(self) -> float:
        return self._order.get_cost() + self._insurance()

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nInsurance (5%): +{self._insurance():.2f}€"


class GiftWrapDecorator(OrderDecorator):
    COST = 5.00

    def get_cost(self) -> float:
        return self._order.get_cost() + self.COST

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nGift wrap: +{self.COST:.2f}€"


class DiscountDecorator(OrderDecorator):
    def __init__(self, order: OrderComponent, percent: float):
        super().__init__(order)
        if not 0 <= percent <= 100:
            raise ValueError("Discount must be between 0 and 100")
        self.percent = percent

    def _discount(self) -> float:
        return self._order.get_cost() * self.percent / 100

    def get_cost(self) -> float:
        return self._order.get_cost() - self._discount()

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nDiscount ({self.percent:g}%): -{self._discount():.2f}€"


class PremiumMemberDecorator(DiscountDecorator):
    """A premium member is just a fixed 10% discount: reuse DiscountDecorator."""

    def __init__(self, order: OrderComponent):
        super().__init__(order, percent=10)

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nPremium member (10%): -{self._discount():.2f}€"


if __name__ == "__main__":
    # Simple order
    order = BaseOrder(100.00)
    print(order.get_description())
    print(f"Total: {order.get_cost():.2f}€")

    print("\n---\n")

    # Complex order: readable, and the ORDER of the layers is now explicit
    # (shipping, insurance and gift wrap first, then the discounts apply on top).
    order = BaseOrder(100.00)
    order = InsuranceDecorator(order)
    order = ExpressShippingDecorator(order)
    order = GiftWrapDecorator(order)
    order = DiscountDecorator(order, percent=15)
    order = PremiumMemberDecorator(order)

    print(order.get_description())
    print(f"Total: {order.get_cost():.2f}€")
