import json
import os
import unittest
from unittest.mock import patch

from core import analyze


class FakeResponse:
    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.data


class AnalyzeTests(unittest.TestCase):
    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze("   ")

    def test_oversized_input_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze("x" * 12001)

    def test_missing_api_key_is_rejected(self):
        with patch.dict(os.environ, {"AI_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "AI_API_KEY"):
                analyze("Explain this")

    @patch("urllib.request.urlopen")
    def test_successful_model_response(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({
            "choices": [{"message": {"content": "Example model answer"}}]
        })
        with patch.dict(os.environ, {
            "AI_API_KEY": "test-key",
            "AI_BASE_URL": "https://example.invalid",
            "AI_MODEL": "test-model"
        }):
            result = analyze("Explain a simple example")

        self.assertEqual(result["answer"], "Example model answer")
        self.assertEqual(result["model"], "test-model")
        request = mock_urlopen.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/chat/completions"))
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")

    @patch("urllib.request.urlopen")
    def test_malformed_provider_response_is_rejected(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"unexpected": []})
        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}):
            with self.assertRaisesRegex(RuntimeError, "did not contain"):
                analyze("Test")


if __name__ == "__main__":
    unittest.main()
