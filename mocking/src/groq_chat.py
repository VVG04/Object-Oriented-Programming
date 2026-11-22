"""A function that calls an LLM API (Groq). We never call the real API in tests: we mock it."""

from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def ask_groq(question: str, client: Groq = None) -> str:
    """Send a question to Groq and return the answer.

    `client` is optional: in real life we let the function build a real Groq()
    client, in tests we pass a fake one. Passing a dependency in like this is
    called *dependency injection*, and it is what makes the code easy to test.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty")

    client = client or Groq()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=1024,
    )
    return response.choices[0].message.content
