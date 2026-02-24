# imports 
from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfiguationError

load_dotenv()

def get_project_root() -> Path:
    current_file = Path(__file__)
    return current_file.parent.parent


@dataclass
class CalculatorConfig:

    def __init__(  self, 
    base_dir: Optional[Path] = None,
    max_history_size: Optional[int] = None,
    auto_save: Optional[bool] = None,
    precision: Optional[int] = None,
    max_input_value: Optional[Number] = None,
    default_encoding: Optional[str] = None ): 
    
        project_root = get_project_root()

        self.base_dir = base_dir or Path(
            os.getenv('CALCULATOR_BASE_DIR', project_root).resolve()
        )

        # Set log directory and file paths based on the base directory
        self.max_history_size = max_history_size or int(os.getenv('CALCULATOR_MAX_HISTORY_SIZE', 1000))

        # Determine auto_save setting based on environment variable or provided argument, defaulting to True if not set
        auto_save_env = os.getenv('CALCULATOR_AUTO_SAVE', 'True').lower()

        # Determine auto_save setting based on environment variable or provided argument, defaulting to True if not set
        self.auto_save = auto_save if auto_save is not None else (auto_save_env == 'true')

        # Set precision for Decimal operations, defaulting to 10 if not provided or set in environment variables
        self.precision = precision or int(os.getenv('CALCULATOR_PRECISION', 10))        

        self.max_input_value = max_input_value or Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1E+999'))
        self.default_encoding = default_encoding or os.getenv('CALCULATOR_DEFAULT_ENCODING', 'utf-8')

        @property
        def log_dir(self) -> Path:
            """
            Get log directory path.

            Determines the directory path where log files will be stored.

            Returns:
                Path: The log directory path.
            """
            return Path(os.getenv(
                'CALCULATOR_LOG_DIR',
                str(self.base_dir / "logs")
            )).resolve()

        @property
        def history_dir(self) -> Path:
            """
            Get history directory path.

            Determines the directory path where calculation history files will be stored.

            Returns:
                Path: The history directory path.
            """
            return Path(os.getenv(
                'CALCULATOR_HISTORY_DIR',
                str(self.base_dir / "history")
            )).resolve()

        @property
        def history_file(self) -> Path:
            """
            Get history file path.

            Determines the file path for storing calculation history in CSV format.

            Returns:
                Path: The history file path.
            """
            return Path(os.getenv(
                'CALCULATOR_HISTORY_FILE',
                str(self.history_dir / "calculator_history.csv")
            )).resolve()

        @property
        def log_file(self) -> Path:
            """
            Get log file path.

            Determines the file path for storing log entries.

            Returns:
                Path: The log file path.
            """
            return Path(os.getenv(
                'CALCULATOR_LOG_FILE',
                str(self.log_dir / "calculator.log")
            )).resolve()

        def validate(self) -> None:
            """
            Validate configuration settings.

            Ensures that all configuration parameters meet the required criteria.
            Raises ConfigurationError if any validation fails.

            Raises:
                ConfigurationError: If any configuration parameter is invalid.
            """
            if self.max_history_size <= 0:
                raise ConfigurationError("max_history_size must be positive")
            if self.precision <= 0:
                raise ConfigurationError("precision must be positive")
            if self.max_input_value <= 0:
                raise ConfigurationError("max_input_value must be positive")
            if not self.default_encoding:
                raise ConfigurationError("default_encoding must be specified")
            