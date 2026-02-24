from decimal import Decimal

import pytest

from app import calculator_repl
from app.exceptions import OperationError, ValidationError


class FakeCalculator:
    def __init__(self):
        self.saved = 0
        self.loaded = 0
        self.cleared = 0
        self.undo_result = True
        self.redo_result = True
        self.history_lines = []
        self.perform_result = Decimal("5")
        self.raise_on_save = None
        self.raise_on_load = None
        self.raise_on_perform = None
        self.observers = []
        self.last_operation = None

    def add_observer(self, observer):
        self.observers.append(observer)

    def save_history(self):
        if self.raise_on_save:
            raise self.raise_on_save
        self.saved += 1

    def load_history(self):
        if self.raise_on_load:
            raise self.raise_on_load
        self.loaded += 1

    def show_history(self):
        return self.history_lines

    def clear_history(self):
        self.cleared += 1

    def undo(self):
        return self.undo_result

    def redo(self):
        return self.redo_result

    def set_operation(self, operation):
        self.last_operation = operation

    def perform_operation(self, a, b):
        if self.raise_on_perform:
            raise self.raise_on_perform
        return self.perform_result


def _run_repl_with_inputs(monkeypatch: pytest.MonkeyPatch, commands: list[str], fake_calc: FakeCalculator, capsys):
    monkeypatch.setattr(calculator_repl, "Calculator", lambda: fake_calc)
    monkeypatch.setattr(calculator_repl, "LoggingObserver", lambda: object())
    monkeypatch.setattr(calculator_repl, "AutoSaveObserver", lambda calc: object())
    monkeypatch.setattr(calculator_repl, "OperationFactory", type("F", (), {"create_operation": staticmethod(lambda name: f"op:{name}")}))
    responses = iter(commands)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    calculator_repl.calculator_repl()
    return capsys.readouterr().out


def test_repl_startup_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    class InterruptingCalculator:
        def __init__(self):
            raise KeyboardInterrupt

    monkeypatch.setattr(calculator_repl, "Calculator", InterruptingCalculator)
    calculator_repl.calculator_repl()
    assert "Exiting the Calculator REPL" in capsys.readouterr().out


def test_repl_startup_eof(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    class EofCalculator:
        def __init__(self):
            raise EOFError

    monkeypatch.setattr(calculator_repl, "Calculator", EofCalculator)
    calculator_repl.calculator_repl()
    assert "Exiting the Calculator REPL" in capsys.readouterr().out


def test_repl_startup_generic_error(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    class BadCalculator:
        def __init__(self):
            raise RuntimeError("bad init")

    monkeypatch.setattr(calculator_repl, "Calculator", BadCalculator)
    calculator_repl.calculator_repl()
    assert "An error occurred: bad init" in capsys.readouterr().out


def test_repl_help_then_unknown_then_exit(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    output = _run_repl_with_inputs(monkeypatch, ["help", "wat", "exit"], fake_calc, capsys)

    assert "Available commands:" in output
    assert "Unknown command" in output
    assert "Goodbye!" in output
    assert fake_calc.saved == 1


def test_repl_exit_handles_save_failure(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    fake_calc.raise_on_save = RuntimeError("disk full")
    output = _run_repl_with_inputs(monkeypatch, ["exit"], fake_calc, capsys)
    assert "Failed to save history: disk full" in output


def test_repl_history_empty_and_non_empty(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    output_1 = _run_repl_with_inputs(monkeypatch, ["history", "exit"], fake_calc, capsys)
    assert "No calculations performed yet." in output_1

    fake_calc = FakeCalculator()
    fake_calc.history_lines = ["1 + 2 = 3"]
    output_2 = _run_repl_with_inputs(monkeypatch, ["history", "exit"], fake_calc, capsys)
    assert "Calculation History:" in output_2
    assert "1. 1 + 2 = 3" in output_2


def test_repl_clear_undo_redo_paths(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    fake_calc.undo_result = False
    fake_calc.redo_result = False
    output = _run_repl_with_inputs(monkeypatch, ["clear", "undo", "redo", "exit"], fake_calc, capsys)

    assert fake_calc.cleared == 1
    assert "Nothing to undo." in output
    assert "Nothing to redo." in output


def test_repl_save_and_load_success_and_failure(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    fake_calc.raise_on_load = RuntimeError("read fail")
    output = _run_repl_with_inputs(monkeypatch, ["save", "load", "exit"], fake_calc, capsys)
    assert "History saved successfully." in output
    assert "Failed to load history: read fail" in output


def test_repl_save_command_failure_branch(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    fake_calc.raise_on_save = RuntimeError("cannot write")
    output = _run_repl_with_inputs(monkeypatch, ["save", "exit"], fake_calc, capsys)
    assert "Failed to save history: cannot write" in output


def test_repl_load_success_branch(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    output = _run_repl_with_inputs(monkeypatch, ["load", "exit"], fake_calc, capsys)
    assert "History loaded successfully." in output


def test_repl_add_flow_success(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    output = _run_repl_with_inputs(monkeypatch, ["add", "2", "3", "exit"], fake_calc, capsys)

    assert fake_calc.last_operation == "op:add"
    assert "Result: 5" in output


def test_repl_add_cancel_paths(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    output = _run_repl_with_inputs(monkeypatch, ["add", "cancel", "add", "2", "cancel", "exit"], fake_calc, capsys)
    assert output.count("Operation cancelled.") == 2


def test_repl_add_validation_operation_and_unexpected_errors(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    fake_calc.raise_on_perform = ValidationError("bad data")
    output_1 = _run_repl_with_inputs(monkeypatch, ["add", "2", "3", "exit"], fake_calc, capsys)
    assert "Operation failed: bad data" in output_1

    fake_calc = FakeCalculator()
    fake_calc.raise_on_perform = RuntimeError("boom")
    output_2 = _run_repl_with_inputs(monkeypatch, ["add", "2", "3", "exit"], fake_calc, capsys)
    assert "Unexpected error: boom" in output_2


def test_repl_loop_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()

    monkeypatch.setattr(calculator_repl, "Calculator", lambda: fake_calc)
    monkeypatch.setattr(calculator_repl, "LoggingObserver", lambda: object())
    monkeypatch.setattr(calculator_repl, "AutoSaveObserver", lambda calc: object())

    def raise_interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)
    calculator_repl.calculator_repl()
    assert "Exiting the Calculator REPL" in capsys.readouterr().out


def test_repl_loop_eof(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()

    monkeypatch.setattr(calculator_repl, "Calculator", lambda: fake_calc)
    monkeypatch.setattr(calculator_repl, "LoggingObserver", lambda: object())
    monkeypatch.setattr(calculator_repl, "AutoSaveObserver", lambda calc: object())

    def raise_eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    calculator_repl.calculator_repl()
    assert "Exiting the Calculator REPL" in capsys.readouterr().out


def test_repl_add_handles_operation_error_type(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    fake_calc = FakeCalculator()
    fake_calc.raise_on_perform = OperationError("cannot divide")
    output = _run_repl_with_inputs(monkeypatch, ["add", "2", "3", "exit"], fake_calc, capsys)
    assert "Operation failed: cannot divide" in output
