# Exercise 6 (slide 93): Testing and mocking with pytest

**Statement:** [courses.dallard.tech/ci_cd/testing_python_intro](https://courses.dallard.tech/ci_cd/testing_python_intro/)
**Result:** 32 tests pass, 1 is skipped on purpose (it needs a real API key), coverage 100%.

```bash
cd mocking
pip install -r requirements.txt
pytest                                   # run everything
pytest --cov=src --cov-report=term-missing   # + coverage report
pytest -m "not slow"                     # skip tests marked slow
pytest -m slow                           # ONLY the slow tests
```

> Note: the course page writes `pytest --markers=slow` to run only slow tests. That is a typo.
> `pytest --markers` **lists** the markers; `pytest -m slow` **runs** the marked tests.

## Folder layout (the "solid project structure" from the page)

```
mocking/
├── src/                       # the code we test
│   ├── app.py                 # e-commerce example (functions + 2 classes)
│   └── groq_chat.py           # a function that calls an LLM API
├── tests/
│   ├── conftest.py            # shared fixtures (repo, order_service, fake_groq_client)
│   ├── test_unit_app.py       # unit tests
│   ├── test_integration_app.py# integration tests
│   └── test_groq_chat.py      # mocking tests
├── pyproject.toml             # pytest settings + the "slow" marker
└── requirements.txt
```

---

## 1. The testing pyramid

| Level | Tests what | Speed | How many | Here |
| --- | --- | --- | --- | --- |
| **Unit** | ONE function or class, alone | Very fast | Most of them | `calculate_discount`, `calculate_tax`, `calculate_total`, `ProductRepository` |
| **Integration** | Several pieces working together | Slower | Fewer | `OrderService` + `ProductRepository` + the calculation functions |
| **End-to-end** | The whole app like a real user (clicks, forms) | Slowest | A few | Not done in pytest: tools like Playwright or Selenium |

Rule of thumb for the exam: if a test touches only one function and no outside world, it is a **unit** test.
If a bug could come from how two parts talk to each other, you need an **integration** test.

## 2. How a pytest test works

- A test is a function whose name starts with `test_`, in a file named `test_*.py`. pytest finds them by itself.
- `assert something` is the check. If it is false, the test fails and pytest shows both values.
- `with pytest.raises(ValueError, match="..."):` checks that the code **does** raise the right error.
- `@pytest.mark.parametrize("x", [a, b, c])` runs the same test once per value (see `test_unit_out_of_range_discounts_rejected`).

**AAA pattern**: each test has 3 parts, **Arrange** (prepare data), **Act** (call the code), **Assert** (check). See `test_unit_custom_tax_rate_total`.

## 3. Fixtures and `conftest.py`

A **fixture** is a function that prepares data for tests. A test asks for it just by naming it as a parameter:

```python
@pytest.fixture
def order_service(repo):          # a fixture can use another fixture
    return OrderService(repo)

def test_integration_successful_order(order_service):   # pytest passes it in
    ...
```

Each test gets a **fresh** fixture, so the stock bought in one test never leaks into the next one.
Putting fixtures in `conftest.py` shares them with every test file, with no import needed.

## 4. Mocking (the most important part)

**Problem:** `ask_groq()` calls a paid LLM API. Calling it in tests would need a key and internet, cost money, be slow, and the answer changes every time.

**Solution:** replace the real client with a **Mock**, a fake object that accepts any attribute or call and returns what we tell it to.

```python
mock_client = mocker.Mock()
mock_client.chat.completions.create.return_value = mock_response   # "when called, return this"
mock_client.chat.completions.create.side_effect = Exception("API down")  # "when called, raise this"
```

The 3 mocking tests from the page, plus 2 extras:

| Test | What it proves |
| --- | --- |
| `test_ask_groq` | Our code reads `response.choices[0].message.content` correctly. |
| `test_ask_groq_calls_api_correctly` | Our code sends the right model, messages and `max_tokens` (`assert_called_once_with`). |
| `test_ask_groq_raises_error_when_api_fails` | If the API is down, the error reaches the caller (`side_effect`). |
| Extra: `..._rejects_empty_question_without_calling_api` | An empty question raises `ValueError` and the API is **never** called (`assert_not_called`). |
| Extra: `..._default_client_is_patched` | Without a `client` argument, we use `mocker.patch("src.groq_chat.Groq")` to swap the class itself. |

**Two ways to mock**, worth knowing for the exam:

1. **Dependency injection**: the function takes the client as a parameter (`client=None`), so the test simply passes a fake one. Clean and simple, and why `ask_groq` was written that way.
2. **Patching**: `mocker.patch("module.Name")` replaces a name for the duration of the test. Patch it **where it is used** (`src.groq_chat.Groq`), not where it was defined (`groq.Groq`).

**Mocking rule:** you test that *your code* sends the right request and handles the answer. Whether the LLM's answer is correct is the API's job.

## 5. The other tools on the page

| Tool | One-line idea | Used here |
| --- | --- | --- |
| **Markers** | Tag tests to run groups of them: `@pytest.mark.slow` | Yes, `test_ask_groq_real_api` (skipped without `GROQ_API_KEY`) |
| **Coverage** (`pytest-cov`) | % of code lines run by the tests | Yes, `--cov=src`, 100% |
| **tox** | Run the tests on several Python versions | No (concept only) |
| **Locust** | Load testing: how many requests before the system slows down | No (concept only) |

Never put an API key in the repo. Use an environment variable (`export GROQ_API_KEY=...`). `.env` is in `.gitignore` for that reason.

---

## Check yourself (exam style)

1. Unit, integration or E2E? (a) checking `calculate_tax(100) == 20`; (b) placing an order and checking the stock went down; (c) a robot clicking "Buy" on the website.
2. What is the difference between `return_value` and `side_effect` on a Mock?
3. Why do we mock the LLM API instead of calling it?
4. What does `@pytest.fixture` give you, and why put fixtures in `conftest.py`?
5. You wrote `mocker.patch("groq.Groq")` but the real API is still called. Why?

<details>
<summary>Answers</summary>

1. (a) unit, (b) integration, (c) end-to-end.
2. `return_value` is what the mock returns when called; `side_effect` makes it raise an exception (or run a function, or return values one by one).
3. Real calls are slow, cost money, need a key and internet, fail when the provider is down, and give a different answer each time, so the test can't check an exact value.
4. Reusable, fresh setup data injected by name into tests; `conftest.py` shares it with every test file without imports and avoids copy-paste.
5. `groq_chat.py` did `from groq import Groq`, so it has its own name `Groq`. You must patch where it is used: `mocker.patch("src.groq_chat.Groq")`.

</details>
