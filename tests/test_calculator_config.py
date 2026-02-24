from decimal import Decimal
from pathlib import Path

import pytest

from app.calculator_config import CalculatorConfig, get_project_root
from app.exceptions import ConfigurationError


def test_get_project_root_points_to_repository_root() -> None:
    root = get_project_root()
    assert (root / "app").exists()
    assert (root / "tests").exists()


def test_config_uses_defaults_when_not_provided(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.delenv("CALCULATOR_AUTO_SAVE", raising=False)
    monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    monkeypatch.delenv("CALCULATOR_PRECISION", raising=False)
    monkeypatch.delenv("CALCULATOR_MAX_INPUT_VALUE", raising=False)
    monkeypatch.delenv("CALCULATOR_DEFAULT_ENCODING", raising=False)

    config = CalculatorConfig()

    assert config.base_dir == tmp_path.resolve()
    assert config.max_history_size == 1000
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == Decimal("1E+999")
    assert config.default_encoding == "utf-8"


def test_config_honors_explicit_values_over_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path / "env_base"))
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "7")
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")

    config = CalculatorConfig(
        base_dir=tmp_path / "explicit_base",
        max_history_size=2,
        auto_save=False,
        precision=6,
        max_input_value=Decimal("999"),
        default_encoding="latin-1",
    )

    assert config.base_dir == (tmp_path / "explicit_base").resolve()
    assert config.max_history_size == 2
    assert config.auto_save is False
    assert config.precision == 6
    assert config.max_input_value == Decimal("999")
    assert config.default_encoding == "latin-1"


def test_config_auto_save_false_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    config = CalculatorConfig()
    assert config.auto_save is False


def test_config_path_properties_use_environment_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "custom_logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "custom_history"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "custom_history" / "h.csv"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(tmp_path / "custom_logs" / "c.log"))

    config = CalculatorConfig()

    assert config.log_dir == (tmp_path / "custom_logs").resolve()
    assert config.history_dir == (tmp_path / "custom_history").resolve()
    assert config.history_file == (tmp_path / "custom_history" / "h.csv").resolve()
    assert config.log_file == (tmp_path / "custom_logs" / "c.log").resolve()


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"max_history_size": 0}, "max_history_size must be positive"),
        ({"precision": 0}, "precision must be positive"),
        ({"max_input_value": Decimal("0")}, "max_input_value must be positive"),
    ],
)
def test_config_validation_errors(kwargs: dict, expected: str, tmp_path: Path) -> None:
    base = {
        "base_dir": tmp_path,
        "max_history_size": 1,
        "auto_save": True,
        "precision": 1,
        "max_input_value": Decimal("1"),
        "default_encoding": "utf-8",
    }
    base.update(kwargs)

    with pytest.raises(ConfigurationError, match=expected):
        CalculatorConfig(**base)


def test_config_validation_error_for_empty_default_encoding_from_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "")
    with pytest.raises(ConfigurationError, match="default_encoding must be specified"):
        CalculatorConfig(
            base_dir=tmp_path,
            max_history_size=1,
            auto_save=True,
            precision=1,
            max_input_value=Decimal("1"),
            default_encoding=None,
        )
