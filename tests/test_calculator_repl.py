from app import calculator_repl


def test_repl_exits_on_keyboard_interrupt(monkeypatch, capsys) -> None:
	class InterruptingCalculator:
		def __init__(self):
			raise KeyboardInterrupt

	monkeypatch.setattr(calculator_repl, "Calculator", InterruptingCalculator)

	calculator_repl.calculator_repl()

	captured = capsys.readouterr()
	assert "Exiting the Calculator REPL" in captured.out


def test_repl_exits_on_eof_error(monkeypatch, capsys) -> None:
	class EofCalculator:
		def __init__(self):
			raise EOFError

	monkeypatch.setattr(calculator_repl, "Calculator", EofCalculator)

	calculator_repl.calculator_repl()

	captured = capsys.readouterr()
	assert "Exiting the Calculator REPL" in captured.out

