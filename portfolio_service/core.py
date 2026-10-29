"""OpenAI-compatible model client. API credentials are read from environment variables."""
import json
import os
import urllib.error
import urllib.request

PROJECT_NAME = "InvestEdge AI Market Intelligence"
PROJECT_INSTRUCTIONS = """Analyze market information and explain trends, risks, assumptions, and uncertainty. Do not claim to have live market data unless it is provided in the input. Do not present output as guaranteed returns or personalized financial advice."""


def analyze(text):
    """Send text to a configured OpenAI-compatible chat-completions endpoint."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty.")
    if len(text) > 12000:
        raise ValueError("Input is too long; maximum length is 12000 characters.")

    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("AI_API_KEY is not configured.")

    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("AI_MODEL", "deepseek-chat").strip()
    if not model:
        raise ValueError("AI_MODEL is not configured.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": PROJECT_INSTRUCTIONS},
            {"role": "user", "content": text.strip()}
        ],
        "temperature": 0.2
    }
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("AI provider returned HTTP status " + str(exc.code)) from None
    except urllib.error.URLError:
        raise RuntimeError("Could not connect to the AI provider. Check the endpoint and network.") from None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise RuntimeError("The AI provider returned an invalid response.") from None

    try:
        answer = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("The AI provider response did not contain a chat answer.") from None

    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("The AI provider returned an empty answer.")

    return {
        "project": PROJECT_NAME,
        "model": model,
        "answer": answer.strip(),
        "disclaimer": "AI-generated output may be incorrect. Review it before relying on it."
    }
