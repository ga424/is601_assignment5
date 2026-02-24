from decimal import Decimal
import datetime

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


@pytest.mark.parametrize(
	"operation,a,b,expected",
	[
		("Addition", "2", "3", Decimal("5")),
		("Subtraction", "8", "5", Decimal("3")),
		("Multiplication", "2", "4", Decimal("8")),
		("Division", "10", "2", Decimal("5")),
		("Power", "2", "3", Decimal("8")),
	],
)
def test_calculation_computes_supported_operations(
	operation: str,
	a: str,
	b: str,
	expected: Decimal,
) -> None:
	calc = Calculation(operation=operation, operand1=Decimal(a), operand2=Decimal(b))
	assert calc.result == expected


def test_calculation_root_computes_expected_value(calc_factory) -> None:
	calc = calc_factory(operation="Root", operand1="9", operand2="2")
	assert calc.result == pytest.approx(Decimal("3"))


def test_calculation_unsupported_operation_raises_operation_error(calc_factory) -> None:
	with pytest.raises(OperationError, match="Unsupported operation"):
		calc_factory(operation="Modulo", operand1="10", operand2="3")


def test_calculation_division_by_zero_raises_operation_error(calc_factory) -> None:
	with pytest.raises(OperationError, match="Invalid operation"):
		calc_factory(operation="Division", operand1="1", operand2="0")


@pytest.mark.parametrize(
	"operand1,operand2",
	[
		(Decimal("-4"), Decimal("2")),
		(Decimal("4"), Decimal("0")),
	],
)
def test_calculation_invalid_root_raises_operation_error(
	operand1: Decimal,
	operand2: Decimal,
) -> None:
	with pytest.raises((OperationError, AttributeError)):
		Calculation(operation="Root", operand1=operand1, operand2=operand2)


def test_calculation_str_contains_operation_and_result(calc_factory) -> None:
	calc = calc_factory()
	rendered = str(calc)
	assert "Addition" in rendered
	assert "result=Decimal('3')" in rendered


def test_calculation_to_dict_contains_expected_keys(calc_factory) -> None:
	calc = calc_factory()
	payload = calc.to_dict()
	assert payload["operation"] == "Addition"
	assert payload["operand1"] == "1"
	assert payload["operand2"] == "2"
	assert payload["result"] == "3"
	assert "timestamp" in payload


def test_calculation_from_dict_happy_path(calc_factory) -> None:
	original = calc_factory()
	payload = original.to_dict()

	loaded = Calculation.from_dict(payload)

	assert loaded.operation == original.operation
	assert loaded.operand1 == original.operand1
	assert loaded.operand2 == original.operand2
	assert loaded.timestamp == datetime.datetime.fromisoformat(payload["timestamp"])


def test_calculation_from_dict_logs_warning_on_result_mismatch(caplog: pytest.LogCaptureFixture) -> None:
	caplog.set_level("WARNING")
	payload = {
		"operation": "Addition",
		"operand1": "1",
		"operand2": "2",
		"result": "99",
		"timestamp": "2026-01-01T00:00:00",
	}

	loaded = Calculation.from_dict(payload)

	assert loaded.result == Decimal("3")
	assert "does not match saved result" in caplog.text


@pytest.mark.parametrize(
	"bad_payload",
	[
		{"operation": "Addition", "operand1": "1", "operand2": "2", "result": "3"},
		{"operation": "Addition", "operand1": "abc", "operand2": "2", "result": "3", "timestamp": "2026-01-01T00:00:00"},
	],
)
def test_calculation_from_dict_invalid_payload_raises_operation_error(bad_payload: dict) -> None:
	with pytest.raises(OperationError, match="Invalid data for creating Calculation"):
		Calculation.from_dict(bad_payload)


def test_calculation_raise_invalid_root_fallback_branch() -> None:
	with pytest.raises(OperationError, match="Invalid root operation"):
		Calculation._raise_invalid_root(Decimal("4"), Decimal("-2"))

