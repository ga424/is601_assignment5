import pytest

from app.exceptions import (
	CalculatorError,
	ConfigurationError,
	OperationError,
	ValidationError,
)


def test_validation_error_inheritance() -> None:
	assert issubclass(ValidationError, CalculatorError)


def test_operation_error_inheritance() -> None:
	assert issubclass(OperationError, CalculatorError)


def test_configuration_error_inheritance() -> None:
	assert issubclass(ConfigurationError, CalculatorError)


@pytest.mark.parametrize(
	"exc_type,message",
	[
		(ValidationError, "bad input"),
		(OperationError, "failed op"),
		(ConfigurationError, "bad config"),
	],
)
def test_custom_exception_message(exc_type: type[Exception], message: str) -> None:
	with pytest.raises(exc_type, match=message):
		raise exc_type(message)

