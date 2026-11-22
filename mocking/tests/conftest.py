"""Fixtures shared by every test file. pytest finds this file automatically."""

import pytest

from src.app import OrderService, ProductRepository


@pytest.fixture
def repo():
    """A brand-new fake database for each test, so tests never affect each other."""
    return ProductRepository()


@pytest.fixture
def order_service(repo):
    """An OrderService wired to the fresh repo above (fixtures can use other fixtures)."""
    return OrderService(repo)


@pytest.fixture
def fake_groq_client(mocker):
    """A fake Groq client whose answer is always "4".

    The real response looks like: response.choices[0].message.content
    so we build Mock objects with exactly that shape.
    """
    mock_choice = mocker.Mock()
    mock_choice.message.content = "4"

    mock_response = mocker.Mock()
    mock_response.choices = [mock_choice]

    mock_client = mocker.Mock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client
