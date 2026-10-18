"""Regression: Gradio supplies complete chat context on sequential turns."""

import app
import bot_core as bot


def test_chat_ui_restores_context_from_session_state(monkeypatch):
    observed_histories = []

    def fake_agent(message, history=None, state=None, reflection=True, client=None):
        observed_histories.append(list(history or []))
        if "What project" in message:
            prior = " ".join(turn["content"] for turn in history or [])
            assert "ESP32" in prior
            assert "motion" in prior
            return "You described an ESP32 smart home project with motion sensors.", {}, "memory observed"
        return "I can help with your project.", {}, "first turn"

    monkeypatch.setattr(app, 'handle_turn', fake_agent)
    first = "I am building an ESP32 smart home project with motion and temperature sensors."
    _, shown, session_state, _ = app.chat_ui(first, [], {}, False)
    assert len(shown) == 2
    assert len(session_state["_conversation_history"]) == 2

    # Simulate Gradio returning no visible transcript on the second callback;
    # the separate session_state must still supply both previous messages.
    _, shown, session_state, _ = app.chat_ui("What project did I describe?", [], session_state, False)
    assert len(observed_histories) == 2
    assert len(observed_histories[0]) == 0
    assert len(observed_histories[1]) == 2
    assert len(shown) == 4
    assert len(session_state["_conversation_history"]) == 4


def test_gemini_history_payload_contains_both_roles(monkeypatch):
    # Supply a light-weight stand-in for the Gemini Content classes so this
    # history-serialization test runs offline without installing the SDK.
    import sys
    from types import ModuleType, SimpleNamespace

    class MockPart:
        @staticmethod
        def from_text(text):
            return SimpleNamespace(text=text)

    class MockContent:
        def __init__(self, role, parts):
            self.role = role
            self.parts = parts

    package = ModuleType('google.genai')
    package.types = SimpleNamespace(Content=MockContent, Part=MockPart)
    monkeypatch.setitem(sys.modules, 'google.genai', package)
    history = [
        {"role": "user", "content": "I am building an ESP32 smart home project."},
        {"role": "assistant", "content": "I recommend sensor modules."},
    ]
    contents = bot._recent_contents(history, "What project did I describe?")
    assert [c.role for c in contents] == ["user", "model", "user"]
    assert "ESP32" in contents[0].parts[0].text
    assert "What project" in contents[-1].parts[0].text
