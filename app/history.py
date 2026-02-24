########################
# History Management    #
########################

from abc import ABC, abstractmethod
import logging
from typing import Any
from app.calculation import Calculation


class HistoryObserver(ABC):
    
    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        pass  # pragma: no cover


class LoggingObserver(HistoryObserver):
    # This observer logs the details of each calculation performed, including the operation, operands, and result. 
    # It uses Python's built-in logging module to record this information in a log file or console output, depending on the logging configuration.
    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = "
            f"{calculation.result}"
        )


class AutoSaveObserver(HistoryObserver):
    # This observer automatically saves the calculation history after each operation. 
    # It interacts with the calculator's configuration to determine if auto-saving is enabled and calls the appropriate method to save the history to a file or database.
    def __init__(self, calculator: Any):
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")