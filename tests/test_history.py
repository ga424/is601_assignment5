import pytest

from app.history import AutoSaveObserver, LoggingObserver


def test_logging_observer_logs_calculation(
	caplog: pytest.LogCaptureFixture,
	calc_factory,
) -> None:
	caplog.set_level("INFO")
	observer = LoggingObserver()
	calc = calc_factory()

	observer.update(calc)

	assert "Calculation performed" in caplog.text


def test_logging_observer_none_calculation_raises() -> None:
	observer = LoggingObserver()

	with pytest.raises(AttributeError, match="cannot be None"):
		observer.update(None)


def test_autosave_observer_requires_expected_calculator_interface() -> None:
	with pytest.raises(TypeError, match="must have 'config' and 'save_history'"):
		AutoSaveObserver(object())


def test_autosave_observer_calls_save_history_when_enabled(
	calc_factory,
	fake_calculator_factory,
) -> None:
	calls: list[str] = []
	fake_calculator = fake_calculator_factory(auto_save=True, calls=calls)
	observer = AutoSaveObserver(fake_calculator)

	observer.update(calc_factory())

	assert calls == ["saved"]


def test_autosave_observer_does_not_save_when_disabled(
	calc_factory,
	fake_calculator_factory,
) -> None:
	calls: list[str] = []
	fake_calculator = fake_calculator_factory(auto_save=False, calls=calls)
	observer = AutoSaveObserver(fake_calculator)

	observer.update(calc_factory())

	assert calls == []


def test_autosave_observer_none_calculation_raises(fake_calculator_factory) -> None:
	fake_calculator = fake_calculator_factory(auto_save=True, calls=[])
	observer = AutoSaveObserver(fake_calculator)

	with pytest.raises(AttributeError, match="cannot be None"):
		observer.update(None)

