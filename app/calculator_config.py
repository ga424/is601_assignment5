from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

load_dotenv()


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@dataclass
class CalculatorConfig:
    base_dir: Optional[Path] = None
    max_history_size: Optional[int] = None
    auto_save: Optional[bool] = None
    precision: Optional[int] = None
    max_input_value: Optional[Number] = None
    default_encoding: Optional[str] = None

    def __post_init__(self) -> None:
        project_root = get_project_root()

        self.base_dir = Path(
            self.base_dir or os.getenv("CALCULATOR_BASE_DIR", str(project_root))
        ).resolve()

        self.max_history_size = (
            self.max_history_size
            if self.max_history_size is not None
            else int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"))
        )

        auto_save_env = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower()
        self.auto_save = (
            self.auto_save if self.auto_save is not None else auto_save_env == "true"
        )

        self.precision = (
            self.precision
            if self.precision is not None
            else int(os.getenv("CALCULATOR_PRECISION", "10"))
        )

        self.max_input_value = (
            self.max_input_value
            if self.max_input_value is not None
            else Decimal(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1E+999"))
        )

        self.default_encoding = (
            self.default_encoding or os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
        )

        self.validate()

    @property
    def log_dir(self) -> Path:
        return Path(
            os.getenv("CALCULATOR_LOG_DIR", str(self.base_dir / "logs"))
        ).resolve()

    @property
    def history_dir(self) -> Path:
        return Path(
            os.getenv("CALCULATOR_HISTORY_DIR", str(self.base_dir / "history"))
        ).resolve()

    @property
    def history_file(self) -> Path:
        return Path(
            os.getenv(
                "CALCULATOR_HISTORY_FILE",
                str(self.history_dir / "calculator_history.csv"),
            )
        ).resolve()

    @property
    def log_file(self) -> Path:
        return Path(
            os.getenv("CALCULATOR_LOG_FILE", str(self.log_dir / "calculator.log"))
        ).resolve()

    def validate(self) -> None:
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")
        if not self.default_encoding:
            raise ConfigurationError("default_encoding must be specified")
