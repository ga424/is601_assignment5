from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.calculation import Calculation
from app.history import AutoSaveObserver, LoggingObserver


def _sample_calculation() -> Calculation:
	return Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))


def test_logging_observer_logs_calculation(caplog: pytest.LogCaptureFixture) -> None:
	caplog.set_level("INFO")
	observer = LoggingObserver()
	calc = _sample_calculation()

	observer.update(calc)

	assert "Calculation performed" in caplog.text


def test_logging_observer_none_calculation_raises() -> None:
	observer = LoggingObserver()

	with pytest.raises(AttributeError, match="cannot be None"):
		observer.update(None)


def test_autosave_observer_requires_expected_calculator_interface() -> None:
	with pytest.raises(TypeError, match="must have 'config' and 'save_history'"):
		AutoSaveObserver(object())


def test_autosave_observer_calls_save_history_when_enabled() -> None:
	calls: list[str] = []

	def save_history() -> None:
		calls.append("saved")

	fake_calculator = SimpleNamespace(
		config=SimpleNamespace(auto_save=True),
		save_history=save_history,
	)
	observer = AutoSaveObserver(fake_calculator)

	observer.update(_sample_calculation())

	assert calls == ["saved"]


def test_autosave_observer_does_not_save_when_disabled() -> None:
	calls: list[str] = []

	def save_history() -> None:
		calls.append("saved")

	fake_calculator = SimpleNamespace(
		config=SimpleNamespace(auto_save=False),
		save_history=save_history,
	)
	observer = AutoSaveObserver(fake_calculator)

	observer.update(_sample_calculation())

	assert calls == []


def test_autosave_observer_none_calculation_raises() -> None:
	fake_calculator = SimpleNamespace(
		config=SimpleNamespace(auto_save=True),
		save_history=lambda: None,
	)
	observer = AutoSaveObserver(fake_calculator)

	with pytest.raises(AttributeError, match="cannot be None"):
		observer.update(None)

