import json

import pytest

from adapter_report import (
    AnalyticsDashboard,
    LegacyReportAdapter,
    LegacyReportGenerator,
    ReportGeneratorInterface,
)
from decorator_order import (
    BaseOrder,
    DiscountDecorator,
    ExpressShippingDecorator,
    GiftWrapDecorator,
    InsuranceDecorator,
    OrderComponent,
    PremiumMemberDecorator,
)


# ---- Adapter -------------------------------------------------------------------
def test_adapter_returns_json_with_original_types():
    adapter = LegacyReportAdapter(LegacyReportGenerator())
    data = {"total_sales": 150000, "orders": 1234, "avg_order": 121.55, "region": "EU"}
    assert json.loads(adapter.generate(data)) == data


def test_adapter_implements_interface():
    assert isinstance(LegacyReportAdapter(LegacyReportGenerator()), ReportGeneratorInterface)


def test_adapter_really_calls_the_legacy_system(mocker):
    legacy = mocker.Mock()
    legacy.generate_report.return_value = "<report>\n  <orders>3</orders>\n</report>"
    assert json.loads(LegacyReportAdapter(legacy).generate({"ignored": 1})) == {"orders": 3}
    legacy.generate_report.assert_called_once_with({"ignored": 1})


def test_dashboard_accepts_adapter_output(capsys):
    AnalyticsDashboard().display(LegacyReportAdapter(LegacyReportGenerator()).generate({"orders": 7}))
    assert "orders: 7" in capsys.readouterr().out


# ---- Decorator -----------------------------------------------------------------
def test_base_order():
    assert BaseOrder(100).get_cost() == 100


@pytest.mark.parametrize(
    "wrap, expected",
    [
        (ExpressShippingDecorator, 115),
        (InsuranceDecorator, 105),
        (GiftWrapDecorator, 105),
        (PremiumMemberDecorator, 90),
        (lambda o: DiscountDecorator(o, percent=15), 85),
    ],
)
def test_each_decorator_alone(wrap, expected):
    assert wrap(BaseOrder(100)).get_cost() == pytest.approx(expected)


def test_full_order_matches_the_legacy_result():
    # Legacy code: 100 + 15 + 5 (5% of base) + 5 = 125; -15% = 106.25; -10% = 95.625
    order = PremiumMemberDecorator(
        DiscountDecorator(GiftWrapDecorator(ExpressShippingDecorator(InsuranceDecorator(BaseOrder(100)))), percent=15)
    )
    assert order.get_cost() == pytest.approx(95.625)
    assert isinstance(order, OrderComponent)


def test_layer_order_matters():
    # Discount THEN shipping is not the same as shipping THEN discount.
    a = ExpressShippingDecorator(DiscountDecorator(BaseOrder(100), percent=10)).get_cost()  # 90 + 15
    b = DiscountDecorator(ExpressShippingDecorator(BaseOrder(100)), percent=10).get_cost()  # 115 * 0.9
    assert (a, b) == (pytest.approx(105), pytest.approx(103.5))


def test_description_lists_every_layer():
    text = GiftWrapDecorator(ExpressShippingDecorator(BaseOrder(100))).get_description()
    assert text.splitlines() == ["Base price: 100.00€", "Express shipping: +15.00€", "Gift wrap: +5.00€"]


def test_invalid_discount():
    with pytest.raises(ValueError):
        DiscountDecorator(BaseOrder(100), percent=150)
