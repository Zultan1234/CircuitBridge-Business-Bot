"""API-key-free smoke tests for 3-way routing and both required tools."""
from pathlib import Path
import json
import bot_core as bot


def test_router_three_paths():
    assert bot.route_message("What do you sell?") == "general_question"
    assert bot.route_message("Contact me about a scope") == "lead_collection"
    assert bot.route_message("Feedback: please offer more sensors") == "feedback"
    assert bot.route_message("My email is student@example.com") == "lead_collection"
    assert bot.route_message("Sam", {"pending_lead": True}) == "lead_collection"


def test_quote_uses_catalog_not_guessed():
    q = bot.create_quote("CB-SOLDER-75", 2)
    assert q["status"] == "ok"
    assert q["unit_price_usd"] == 89.0
    assert q["subtotal_usd"] == 178.0
    assert "shipping" in q["excluded"]
    assert bot.create_quote("NOT-A-SKU")["status"] == "error"
    assert bot.create_quote("CB-SOLDER-75", -1)["status"] == "error"
    assert bot.create_quote("CB-SOLDER-75", 2.5)["status"] == "error"


def test_search_budget():
    result = bot.search_catalog("USB-C charger", 40)
    assert result["matches"]
    assert all(p["price_usd"] <= 40 for p in result["matches"])
    assert any(p["sku"] == "CB-PD-65" for p in result["matches"])


def test_record_tools(tmp_path, monkeypatch):
    monkeypatch.setattr(bot, "DATA_DIR", tmp_path)
    lead = bot.record_customer_interest("sam@example.com", "Sam Demo", "Lab equipment")
    assert lead["status"] == "saved"
    assert len((tmp_path / "leads.jsonl").read_text().splitlines()) == 1
    feedback = bot.record_feedback("Do you ship to Mars?")
    assert feedback["status"] == "saved"
    assert json.loads((tmp_path / "feedback.jsonl").read_text().splitlines()[0])["question"] == "Do you ship to Mars?"
    assert bot.record_customer_interest("invalid", "Sam Demo", "Inquiry")["status"] == "error"


def test_multiturn_lead(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "DATA_DIR", tmp_path)
    answer, state, trace = bot.handle_turn("Please contact me about a router", reflection=False)
    assert "name" in answer.lower()
    assert state["pending_lead"]
    answer, state, trace = bot.handle_turn("Sam Demo", state=state, reflection=False)
    assert "email" in answer.lower()
    answer, state, trace = bot.handle_turn("sam@example.com", state=state, reflection=False)
    assert "saved" in answer.lower()
    assert "record_customer_interest" in trace
    assert json.loads((tmp_path / "leads.jsonl").read_text().splitlines()[0])["message"] == "Please contact me about a router"


def test_feedback_route_calls_tool(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "DATA_DIR", tmp_path)
    reply, st, trace = bot.handle_turn("Feedback: your demo needs more filters", reflection=False)
    assert "record_feedback" in trace
    assert "saved" in reply


def test_exact_quote_tool(monkeypatch):
    reply, _, trace = bot.handle_turn("Quote 2 x CB-SOLDER-75", reflection=False)
    assert "$178.00" in reply
    assert "create_quote" in trace
    assert "shipping" in reply.lower()
