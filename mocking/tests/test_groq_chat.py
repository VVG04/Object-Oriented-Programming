"""Mocking tests: we test OUR code (does it send the right request? does it read the
answer correctly? does it handle errors?) without ever calling the real Groq API.

`mocker` is a fixture given by the pytest-mock plugin.
"""

import pytest

from src.groq_chat import ask_groq


# 1. Build the mock ----------------------------------------------------------
def test_ask_groq(mocker):
    # Arrange: a fake response with the same shape as the real one
    mock_choice = mocker.Mock()
    mock_choice.message.content = "4"

    mock_response = mocker.Mock()
    mock_response.choices = [mock_choice]

    # ... and a fake client that returns it
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.return_value = mock_response

    # Act: call our function with the fake client
    answer = ask_groq("What is 2+2?", client=mock_client)

    # Assert
    assert answer == "4"


# 2. Verify the call -----------------------------------------------------------
def test_ask_groq_calls_api_correctly(fake_groq_client):
    # Same fake client, but built once in conftest.py (no copy-paste).
    ask_groq("What is 2+2?", client=fake_groq_client)

    # We check that OUR code sent the right request, not what the LLM answers.
    fake_groq_client.chat.completions.create.assert_called_once_with(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "What is 2+2?"}],
        max_tokens=1024,
    )


# 3. Simulate a failure ---------------------------------------------------------
def test_ask_groq_raises_error_when_api_fails(mocker):
    mock_client = mocker.Mock()
    # side_effect = "when called, raise this instead of returning"
    mock_client.chat.completions.create.side_effect = Exception("API down")

    with pytest.raises(Exception, match="API down"):
        ask_groq("What is 2+2?", client=mock_client)


# Extras -------------------------------------------------------------------------
@pytest.mark.parametrize("empty", ["", "   ", "\n"])
def test_ask_groq_rejects_empty_question_without_calling_api(empty, fake_groq_client):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        ask_groq(empty, client=fake_groq_client)
    # The API must not have been called at all (saves money!)
    fake_groq_client.chat.completions.create.assert_not_called()


def test_ask_groq_default_client_is_patched(mocker, fake_groq_client):
    """When no client is passed, the code creates Groq() itself.

    We can still avoid the real API with mocker.patch: it replaces the name
    `Groq` *where it is used* (in src.groq_chat), not where it is defined.
    """
    fake_groq_class = mocker.patch("src.groq_chat.Groq", return_value=fake_groq_client)

    answer = ask_groq("What is 2+2?")

    assert answer == "4"
    fake_groq_class.assert_called_once_with()  # Groq() was "built" once, with no args


@pytest.mark.slow
def test_ask_groq_real_api():
    """Calls the REAL API. Marked slow and skipped unless a key is set.

    Run only these with:   pytest -m slow
    Run everything else:   pytest -m "not slow"
    """
    import os

    if not os.environ.get("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set: real API test skipped")
    answer = ask_groq("Reply with just the number: what is 2+2?")
    assert "4" in answer
