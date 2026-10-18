"""Regression tests: a Gemini function-call result must be sent back to the LLM.

No network/API key required; simulates SDKs with and without the `id` argument.
"""
import sys
import types as pytypes

import pytest
import bot_core as bot


@pytest.mark.parametrize("supports_id", [False, True])
def test_manual_function_handoff_sdk_variants(monkeypatch, supports_id):
    class LegacyPart:
        @classmethod
        def from_text(cls, *, text):
            return pytypes.SimpleNamespace(text=text)

        @classmethod
        def from_function_response(cls, *, name, response):
            return pytypes.SimpleNamespace(function_response=pytypes.SimpleNamespace(
                name=name, response=response, id=None))

    class ModernPart(LegacyPart):
        @classmethod
        def from_function_response(cls, *, name, response, id=None):
            return pytypes.SimpleNamespace(function_response=pytypes.SimpleNamespace(
                name=name, response=response, id=id))

    class Content:
        def __init__(self, *, role, parts):
            self.role, self.parts = role, parts

    sdk = pytypes.ModuleType("google.genai.types")
    sdk.Part = ModernPart if supports_id else LegacyPart
    sdk.Content = Content
    sdk.Tool = lambda **kw: kw
    sdk.GenerateContentConfig = lambda **kw: kw
    sdk.AutomaticFunctionCallingConfig = lambda **kw: kw
    genai = pytypes.ModuleType("google.genai")
    genai.types = sdk
    google = pytypes.ModuleType("google")
    google.genai = genai
    for name, module in (("google", google), ("google.genai", genai), ("google.genai.types", sdk)):
        monkeypatch.setitem(sys.modules, name, module)

    class Models:
        def __init__(self):
            self.requests = []

        def generate_content(self, *, model, contents, config):
            self.requests.append(contents[:])
            if len(self.requests) == 1:
                function_call = pytypes.SimpleNamespace(
                    name="search_catalog", args={"query": "USB-C charger", "max_price_usd": 40}, id="tool-123")
                return pytypes.SimpleNamespace(
                    function_calls=[function_call], text=None,
                    candidates=[pytypes.SimpleNamespace(content=Content(role="model", parts=[function_call]))])
            return pytypes.SimpleNamespace(function_calls=[], text="The 65 W charger is $34.", candidates=[])

    models = Models()
    client = pytypes.SimpleNamespace(models=models)
    trace = []
    answer = bot.generate_response("Recommend a USB-C charger under $40", [], trace, client=client)
    assert "$34" in answer
    assert "Tool called: search_catalog → ok" in trace
    assert len(models.requests) == 2
    last = models.requests[-1][-1]
    assert last.role == "user"
    assert last.parts[0].function_response.id == "tool-123"
    assert last.parts[0].function_response.response["result"]["status"] == "ok"
