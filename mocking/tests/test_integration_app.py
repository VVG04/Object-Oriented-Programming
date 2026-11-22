"""Integration tests: OrderService + ProductRepository + calculation functions TOGETHER.

The `order_service` fixture comes from conftest.py: a fresh repo for every test.
"""


class TestIntegrationOrderService:
    def test_integration_successful_order(self, order_service):
        result = order_service.place_order("SHIRT", 2)

        assert result["success"] is True
        assert result["item"] == "T-Shirt"
        assert result["quantity"] == 2
        # 2 shirts * 25 = 50, + 20% tax = 60
        assert result["total"] == 60.0

    def test_integration_stock_is_reduced_after_order(self, order_service):
        order_service.place_order("MUG", 3)
        product = order_service.repo.get_product("MUG")

        # started at 100, bought 3 -> 97
        assert product["stock"] == 97

    def test_integration_order_unknown_product(self, order_service):
        result = order_service.place_order("PANTS", 1)

        assert result["success"] is False
        assert result["error"] == "Product not found"

    def test_integration_order_exceeds_stock(self, order_service):
        result = order_service.place_order("HAT", 999)

        assert result["success"] is False
        assert result["error"] == "Not enough stock"

    def test_integration_multiple_orders_deplete_stock(self, order_service):
        """Two successive orders should both reduce stock correctly."""
        order_service.place_order("HAT", 10)
        order_service.place_order("HAT", 15)

        product = order_service.repo.get_product("HAT")
        # started at 30, bought 10 + 15 = 25 -> 5 remaining
        assert product["stock"] == 5

    def test_integration_failed_order_does_not_touch_stock(self, order_service):
        """Extra: a refused order must leave the stock unchanged."""
        order_service.place_order("HAT", 999)
        assert order_service.repo.get_product("HAT")["stock"] == 30

    def test_integration_exact_stock_is_allowed(self, order_service):
        """Extra (boundary): buying exactly what is left works and empties the stock."""
        result = order_service.place_order("HAT", 30)
        assert result["success"] is True
        assert order_service.repo.get_product("HAT")["stock"] == 0
