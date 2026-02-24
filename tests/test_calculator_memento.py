import datetime

import pytest

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def test_memento_from_dict_rehydrates_history(
	monkeypatch: pytest.MonkeyPatch,
	raw_calc_payload: dict,
	calc_factory,
) -> None:
	captured_calls = []

	def fake_from_dict(item: dict) -> Calculation:
		captured_calls.append(item)
		return calc_factory()

	monkeypatch.setattr(Calculation, "from_dict", staticmethod(fake_from_dict), raising=False)

	raw = {
		"history": [raw_calc_payload],
		"timestamp": "2026-01-01T12:00:00",
	}

	memento = CalculatorMemento.from_dict(raw)

	assert len(memento.history) == 1
	assert captured_calls == raw["history"]
	assert memento.timestamp == datetime.datetime.fromisoformat(raw["timestamp"])


def test_memento_to_dict_serializes_history(calc_factory) -> None:
	memento = CalculatorMemento(history=[calc_factory()])

	payload = memento.to_dict()

	assert "history" in payload
	assert len(payload["history"]) == 1
	assert payload["history"][0]["operation"] == "Addition"
	assert "timestamp" in payload

