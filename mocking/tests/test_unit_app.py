"""Unit tests: ONE function at a time, no database, no network. Fast."""

import pytest

from src.app import calculate_discount, calculate_tax, calculate_total


class TestUnitDiscount:
    """Unit tests for calculate_discount()."""

    def test_unit_10_percent_off(self):
        assert calculate_discount(100, 10) == 90.0

    def test_unit_full_price_when_zero_discount(self):
        assert calculate_discount(50, 0) == 50.0

    def test_unit_free_when_100_percent_discount(self):
        assert calculate_discount(75, 100) == 0.0

    def test_unit_handles_decimals(self):
        assert calculate_discount(19.99, 15) == 16.99

    def test_unit_negative_price_raises_error(self):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            calculate_discount(-10, 20)

    def test_unit_invalid_discount_raises_error(self):
        with pytest.raises(ValueError, match="Discount must be between"):
            calculate_discount(100, 150)

    # Extra: the same test run on several inputs thanks to parametrize.
    # Boundaries (0 and 100) are where bugs hide, so we test just outside them.
    @pytest.mark.parametrize("bad_discount", [-1, 101, 150])
    def test_unit_out_of_range_discounts_rejected(self, bad_discount):
        with pytest.raises(ValueError):
            calculate_discount(100, bad_discount)


class TestUnitTax:
    """Unit tests for calculate_tax()."""

    def test_unit_default_20_percent_tax(self):
        assert calculate_tax(100) == 20.0

    def test_unit_custom_tax_rate(self):
        assert calculate_tax(100, 0.10) == 10.0

    def test_unit_zero_price_zero_tax(self):
        assert calculate_tax(0) == 0.0


class TestUnitTotal:
    """Unit tests for calculate_total()."""

    def test_unit_single_item_total(self):
        # 50 + 20% tax = 60
        assert calculate_total([50.0]) == 60.0

    def test_unit_multiple_items_total(self):
        # 10 + 20 + 30 = 60, tax = 12, total = 72
        assert calculate_total([10.0, 20.0, 30.0]) == 72.0

    def test_unit_empty_cart(self):
        assert calculate_total([]) == 0.0

    def test_unit_custom_tax_rate_total(self):
        # Arrange
        prices = [100.0]
        # Act
        total = calculate_total(prices, tax_rate=0.055)
        # Assert: 100 + 5.5 = 105.5
        assert total == 105.5


class TestUnitRepository:
    """Unit tests for ProductRepository on its own (the `repo` fixture is in conftest.py)."""

    def test_unit_update_stock_refuses_too_much(self, repo):
        assert repo.update_stock("HAT", 31) is False
        assert repo.get_product("HAT")["stock"] == 30  # unchanged

    def test_unit_update_stock_unknown_sku(self, repo):
        assert repo.update_stock("PANTS", 1) is False
