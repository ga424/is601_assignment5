import app.exceptions as exceptions
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.calculation import Calculation


if not hasattr(exceptions, "ConfiguationError"):
    exceptions.ConfiguationError = exceptions.ConfigurationError


@pytest.fixture
def calc_factory():
    def _build(
        operation: str = "Addition",
        operand1: str = "1",
        operand2: str = "2",
    ) -> Calculation:
        return Calculation(
            operation=operation,
            operand1=Decimal(operand1),
            operand2=Decimal(operand2),
        )

    return _build


@pytest.fixture
def raw_calc_payload() -> dict:
    return {
        "operation": "Addition",
        "operand1": "1",
        "operand2": "2",
        "result": "3",
        "timestamp": "2026-01-01T00:00:00",
    }


@pytest.fixture
def fake_calculator_factory():
    def _build(auto_save: bool, calls: list[str]):
        def save_history() -> None:
            calls.append("saved")

        return SimpleNamespace(
            config=SimpleNamespace(auto_save=auto_save),
            save_history=save_history,
        )

    return _build
