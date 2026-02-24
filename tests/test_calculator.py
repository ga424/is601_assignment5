from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.operations import Addition


class _Observer:
    def __init__(self) -> None:
        self.events = []

    def update(self, calculation: Calculation) -> None:
        self.events.append(calculation)


def _config(tmp_path: Path, **overrides) -> CalculatorConfig:
    params = {
        "base_dir": tmp_path,
        "max_history_size": 2,
        "auto_save": False,
        "precision": 10,
        "max_input_value": Decimal("100000"),
        "default_encoding": "utf-8",
    }
    params.update(overrides)
    return CalculatorConfig(**params)


def test_calculator_initialization_with_explicit_config(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))

    assert calc.history == []
    assert calc.undo_stack == []
    assert calc.redo_stack == []
    assert calc.config.history_dir.exists()


def test_calculator_initialization_with_default_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    calc = Calculator()
    assert calc.config.base_dir.name == "assignment5"


def test_calculator_init_handles_load_history_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured = []

    def capture_error(message: str) -> None:
        captured.append(message)

    monkeypatch.setattr("logging.error", capture_error)
    monkeypatch.setattr(Calculator, "load_history", lambda self: (_ for _ in ()).throw(Exception("boom")))

    Calculator(config=_config(tmp_path))

    assert captured
    assert "Failed to load existing history" in captured[0]


def test_add_remove_and_notify_observer(tmp_path: Path, calc_factory) -> None:
    calc = Calculator(config=_config(tmp_path))
    observer = _Observer()
    sample = calc_factory()

    calc.add_observer(observer)
    calc.notify_observers(sample)
    calc.remove_observer(observer)
    calc.remove_observer(observer)

    assert observer.events == [sample]


def test_set_operation_and_perform_operation_success(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.set_operation(Addition())

    result = calc.perform_operation("2", "3")

    assert result == Decimal("5")
    assert len(calc.history) == 1
    assert len(calc.undo_stack) == 1


def test_perform_operation_requires_strategy(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    with pytest.raises(OperationError, match="No operation strategy set"):
        calc.perform_operation("1", "2")


def test_perform_operation_wraps_validation_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.set_operation(Addition())

    def fail_validate(value, config):
        raise ValidationError("bad value")

    monkeypatch.setattr("app.calculator.InputValidator.validate_number", fail_validate)

    with pytest.raises(OperationError, match="Input validation error"):
        calc.perform_operation("x", "2")


def test_perform_operation_wraps_unexpected_exception(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.set_operation(Addition())

    monkeypatch.setattr("app.calculator.InputValidator.validate_number", lambda value, config: Decimal("1"))
    monkeypatch.setattr(Addition, "execute", lambda self, a, b: (_ for _ in ()).throw(RuntimeError("explode")))

    with pytest.raises(OperationError, match="Operation error"):
        calc.perform_operation("1", "1")


def test_perform_operation_trims_history_to_max_size(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path, max_history_size=1))
    calc.set_operation(Addition())

    calc.perform_operation("1", "1")
    calc.perform_operation("2", "2")

    assert len(calc.history) == 1
    assert calc.history[0].operand1 == Decimal("2")


def test_save_history_writes_non_empty_csv(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.history = [Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))]

    calc.save_history()

    df = pd.read_csv(calc.config.history_file)
    assert not df.empty
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]


def test_save_history_writes_empty_csv_with_headers(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.history = []

    calc.save_history()

    df = pd.read_csv(calc.config.history_file)
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]


def test_save_history_wraps_exceptions(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    monkeypatch.setattr("pathlib.Path.mkdir", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("denied")))

    with pytest.raises(OperationError, match="Failed to save history"):
        calc.save_history()


def test_load_history_when_file_missing_sets_empty_history(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.history = [Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))]

    calc.load_history()

    assert calc.history == []


def test_load_history_when_file_empty_sets_empty_history(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.config.history_file.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["operation", "operand1", "operand2", "result", "timestamp"]).to_csv(
        calc.config.history_file,
        index=False,
    )

    calc.history = [Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))]
    calc.load_history()
    assert calc.history == []


def test_load_history_reads_existing_records(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.history = [Calculation(operation="Addition", operand1=Decimal("3"), operand2=Decimal("4"))]
    calc.save_history()

    calc.history = []
    calc.load_history()

    assert len(calc.history) == 1
    assert calc.history[0].result == Decimal("7")


def test_load_history_wraps_exceptions(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))

    monkeypatch.setattr("pathlib.Path.exists", lambda self: True)
    monkeypatch.setattr("pandas.read_csv", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad csv")))

    with pytest.raises(OperationError, match="Failed to load history"):
        calc.load_history()


def test_get_history_dataframe_and_show_history_and_get_history(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.history = [Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))]

    frame = calc.get_history_dataframe()
    shown = calc.show_history()
    copied = calc.get_history()

    assert list(frame.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]
    assert "Addition" in shown[0]
    assert copied is not calc.history
    assert copied[0] == calc.history[0]


def test_clear_history_resets_all_stacks(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))
    calc.history = [Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))]
    calc.undo_stack = [CalculatorMemento([])]
    calc.redo_stack = [CalculatorMemento([])]

    calc.clear_history()

    assert calc.history == []
    assert calc.undo_stack == []
    assert calc.redo_stack == []


def test_undo_and_redo_paths(tmp_path: Path) -> None:
    calc = Calculator(config=_config(tmp_path))

    assert calc.undo() is False
    assert calc.redo() is False

    first = Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("1"))
    second = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("2"))

    calc.history = [first, second]
    calc.undo_stack.append(CalculatorMemento([first]))

    assert calc.undo() is True
    assert len(calc.history) == 1
    assert len(calc.redo_stack) == 1

    assert calc.redo() is True
    assert len(calc.history) == 2


def test_setup_logging_error_branch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    calc = object.__new__(Calculator)
    calc.config = _config(tmp_path)

    monkeypatch.setattr("os.makedirs", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("cannot create")))

    with pytest.raises(OSError):
        calc._setup_logging()

    output = capsys.readouterr().out
    assert "Failed to set up logging" in output
