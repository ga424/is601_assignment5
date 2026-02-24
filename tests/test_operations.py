from decimal import Decimal

import pytest

from app.exceptions import ValidationError
from app.operations import (
	Addition,
	Division,
	Multiplication,
	Operation,
	OperationFactory,
	Power,
	Root,
	Subtraction,
)


@pytest.mark.parametrize(
	"operation,a,b,expected",
	[
		(Addition(), Decimal("2"), Decimal("3"), Decimal("5")),
		(Subtraction(), Decimal("10"), Decimal("4"), Decimal("6")),
		(Multiplication(), Decimal("2.5"), Decimal("4"), Decimal("10.0")),
		(Division(), Decimal("9"), Decimal("3"), Decimal("3")),
		(Power(), Decimal("2"), Decimal("3"), Decimal("8")),
	],
)
def test_operations_execute_happy_path(
	operation: Operation,
	a: Decimal,
	b: Decimal,
	expected: Decimal,
) -> None:
	assert operation.execute(a, b) == expected


def test_root_execute_happy_path() -> None:
	result = Root().execute(Decimal("9"), Decimal("2"))
	assert result == pytest.approx(Decimal("3"))


def test_division_by_zero_raises_validation_error() -> None:
	with pytest.raises(ValidationError, match="Division by zero"):
		Division().execute(Decimal("5"), Decimal("0"))


def test_power_negative_exponent_raises_validation_error() -> None:
	with pytest.raises(ValidationError, match="Negative exponents"):
		Power().execute(Decimal("2"), Decimal("-2"))


@pytest.mark.parametrize(
	"a,b,error",
	[
		(Decimal("-4"), Decimal("2"), "negative number"),
		(Decimal("4"), Decimal("0"), "Zero root"),
	],
)
def test_root_validation_errors(a: Decimal, b: Decimal, error: str) -> None:
	with pytest.raises(ValidationError, match=error):
		Root().execute(a, b)


def test_operation_str_returns_class_name() -> None:
	assert str(Addition()) == "Addition"


def test_operation_factory_creates_known_operation() -> None:
	op = OperationFactory.create_operation("add")
	assert isinstance(op, Addition)


def test_operation_factory_is_case_insensitive() -> None:
	op = OperationFactory.create_operation("MuLtIpLy")
	assert isinstance(op, Multiplication)


def test_operation_factory_unknown_operation_raises() -> None:
	with pytest.raises(ValueError, match="Unknown operation"):
		OperationFactory.create_operation("mod")


def test_register_operation_rejects_non_operation_subclass() -> None:
	class NotOperation:
		pass

	with pytest.raises(TypeError, match="inherit from Operation"):
		OperationFactory.register_operation("bad", NotOperation)


def test_register_operation_allows_custom_operation() -> None:
	class Modulo(Operation):
		def execute(self, a: Decimal, b: Decimal) -> Decimal:
			self.validate_operands(a, b)
			return a % b

	OperationFactory.register_operation("mod", Modulo)
	op = OperationFactory.create_operation("mod")
	assert op.execute(Decimal("10"), Decimal("4")) == Decimal("2")

