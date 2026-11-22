import json

import pytest

from builder_employee import DeveloperBuilder, Employee, EmployeeBuilder, InternBuilder
from factory_payment import (
    BankTransferProcessor,
    CreditCardProcessor,
    PaymentFactory,
    PaymentProcessor,
    PayPalProcessor,
)
from singleton_config import ConfigManager


# ---- Factory -------------------------------------------------------------------
@pytest.mark.parametrize(
    "name, cls",
    [("credit_card", CreditCardProcessor), ("bank_transfer", BankTransferProcessor), ("paypal", PayPalProcessor)],
)
def test_factory_returns_right_class(name, cls):
    assert isinstance(PaymentFactory().get_processor(name), cls)


def test_factory_unknown_type():
    with pytest.raises(ValueError, match="Unknown payment type: bitcoin"):
        PaymentFactory().get_processor("bitcoin")


def test_credit_card_fee_is_2_9_percent():
    result = CreditCardProcessor().process(100.0, {"card_number": "1234567890123456", "cvv": "123"})
    assert result == {"success": True, "method": "credit_card", "amount": 102.9, "fee": 2.9}


@pytest.mark.parametrize(
    "details, error",
    [({"card_number": "123", "cvv": "123"}, "Invalid card number"), ({"card_number": "1" * 16, "cvv": "1"}, "Invalid CVV")],
)
def test_credit_card_validation(details, error):
    assert CreditCardProcessor().process(100.0, details) == {"success": False, "error": error}


def test_bank_transfer_flat_fee_and_validation():
    assert BankTransferProcessor().process(100.0, {"iban": "FR7630006000011234567890189"})["fee"] == 1.5
    assert BankTransferProcessor().process(100.0, {"iban": "FR76"})["error"] == "Invalid IBAN"


def test_paypal_fee_and_validation():
    assert PayPalProcessor().process(100.0, {"email": "a@b.com"})["fee"] == 3.7  # 3.4 + 0.30
    assert PayPalProcessor().validate({"email": "nope"}) is False


def test_abstract_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        PaymentProcessor()


# ---- Builder -------------------------------------------------------------------
def test_builder_fluent_chain():
    e = (
        EmployeeBuilder()
        .with_name("John", "Doe")
        .with_email("john.doe@company.com")
        .with_job("Engineering", "Senior Developer", 75000)
        .with_equipment(laptop=True, parking=False)
        .with_access(vpn=True, admin=True)
        .build()
    )
    assert isinstance(e, Employee)
    assert (e.first_name, e.has_laptop, e.has_parking, e.has_admin_rights) == ("John", True, False, True)


def test_each_with_method_returns_the_builder():
    b = EmployeeBuilder()
    assert b.with_name("A", "B") is b


def test_developer_preset_always_has_admin_rights():
    dev = DeveloperBuilder("John", "Doe", "john.doe@company.com").build()
    assert dev.position == "Senior Developer" and dev.has_admin_rights and dev.has_vpn_access


def test_intern_preset():
    intern = InternBuilder("Jane", "Smith", "jane@company.com", "Marketing").with_manager(42).build()
    assert (intern.contract_type, intern.manager_id, intern.has_admin_rights) == ("internship", 42, False)


@pytest.mark.parametrize(
    "builder, message",
    [
        (EmployeeBuilder().with_email("a@b.com").with_job("X", "Y", 1), "Name is required"),
        (EmployeeBuilder().with_name("A", "B").with_email("bad").with_job("X", "Y", 1), "Valid email"),
        (EmployeeBuilder().with_name("A", "B").with_email("a@b.com").with_job("X", "Y", -5), "negative"),
    ],
)
def test_builder_validation(builder, message):
    with pytest.raises(ValueError, match=message):
        builder.build()


# ---- Singleton -----------------------------------------------------------------
@pytest.fixture(autouse=True)
def fresh_singleton():
    ConfigManager.reset()
    yield
    ConfigManager.reset()


def test_singleton_same_instance_and_single_read():
    a = ConfigManager.get_instance()
    b = ConfigManager.get_instance()
    assert a is b
    assert a.load_count == 1


def test_singleton_get_nested_values():
    config = ConfigManager.get_instance()
    assert config.get("database.host") == "localhost"
    assert config.get("database.port") == 5432
    assert config.get("app.debug") is True
    assert config.get("does.not.exist", "default") == "default"


def test_singleton_changes_are_shared():
    ConfigManager.get_instance().set("app.debug", False)
    assert ConfigManager.get_instance().get("app.debug") is False


def test_singleton_direct_construction_is_refused():
    ConfigManager.get_instance()
    with pytest.raises(RuntimeError):
        ConfigManager()


def test_singleton_easy_to_point_at_a_test_file(tmp_path):
    # "Hard to mock in tests" was a problem before: now there is one place to override.
    fake = tmp_path / "config.json"
    fake.write_text(json.dumps({"app": {"name": "TestApp"}}))
    assert ConfigManager.get_instance(fake).get("app.name") == "TestApp"
