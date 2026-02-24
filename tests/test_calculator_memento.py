import datetime
from decimal import Decimal

import pytest

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def test_memento_from_dict_rehydrates_history(monkeypatch: pytest.MonkeyPatch) -> None:
	captured_calls = []

	def fake_from_dict(item: dict) -> Calculation:
		captured_calls.append(item)
		return Calculation(
			operation="Addition",
			operand1=Decimal("1"),
			operand2=Decimal("2"),
		)

	monkeypatch.setattr(Calculation, "from_dict", staticmethod(fake_from_dict), raising=False)

	raw = {
		"history": [
			{
				"operation": "Addition",
				"operand1": "1",
				"operand2": "2",
				"result": "3",
				"timestamp": "2026-01-01T00:00:00",
			}
		],
		"timestamp": "2026-01-01T12:00:00",
	}

	memento = CalculatorMemento.from_dict(raw)

	assert len(memento.history) == 1
	assert captured_calls == raw["history"]
	assert memento.timestamp == datetime.datetime.fromisoformat(raw["timestamp"])


def test_memento_to_dict_currently_raises_type_error() -> None:
	memento = CalculatorMemento(
		history=[
			Calculation(
				operation="Addition",
				operand1=Decimal("1"),
				operand2=Decimal("2"),
			)
		]
	)

	with pytest.raises(TypeError):
		memento.to_dict()

