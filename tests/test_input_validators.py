from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.exceptions import ValidationError
from app.input_validators import InputValidator


def _config(max_value: str = "100") -> SimpleNamespace:
	return SimpleNamespace(max_input_value=Decimal(max_value))


@pytest.mark.parametrize(
	"raw,expected",
	[
		("10", Decimal("1E+1")),
		("  3.5000  ", Decimal("3.5")),
		(12, Decimal("12")),
		("-7", Decimal("-7")),
	],
)
def test_validate_number_accepts_supported_input_types(raw, expected: Decimal) -> None:
	assert InputValidator.validate_number(raw, _config()) == expected


def test_validate_number_rejects_invalid_format() -> None:
	with pytest.raises(ValidationError, match="Invalid number format"):
		InputValidator.validate_number("abc", _config())


def test_validate_number_rejects_values_over_maximum() -> None:
	with pytest.raises(ValidationError, match="exceeds maximum"):
		InputValidator.validate_number("101", _config("100"))


def test_validate_number_allows_value_at_limit() -> None:
	assert InputValidator.validate_number("100", _config("100")) == Decimal("1E+2")

