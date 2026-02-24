from decimal import Decimal

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


def test_calculation_root_computes_expected_value() -> None:
	calc = Calculation(operation="Root", operand1=Decimal("9"), operand2=Decimal("2"))
	assert calc.result == pytest.approx(Decimal("3"))


def test_calculation_unsupported_operation_raises_operation_error() -> None:
	with pytest.raises(OperationError, match="Unsupported operation"):
		Calculation(operation="Modulo", operand1=Decimal("10"), operand2=Decimal("3"))


def test_calculation_division_by_zero_raises_operation_error() -> None:
	with pytest.raises(OperationError, match="Invalid operation"):
		Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("0"))


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


def test_calculation_str_contains_operation_and_result() -> None:
	calc = Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("2"))
	rendered = str(calc)
	assert "Addition" in rendered
	assert "result=Decimal('3')" in rendered

