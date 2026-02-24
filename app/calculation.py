from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict

from app.exceptions import OperationError


@dataclass
class Calculation:
    operation: str
    operand1: Decimal
    operand2: Decimal

    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self) -> None:
        self.result = self.calculate()

    def calculate(self) -> Decimal:
        operations = {
            "Addition": lambda x, y: x + y,
            "Subtraction": lambda x, y: x - y,
            "Multiplication": lambda x, y: x * y,
            "Division": lambda x, y: x / y,
            "Power": lambda x, y: x**y,
            "Root": lambda x, y: (
                Decimal(pow(float(x), 1 / float(y)))
                if x >= 0 and y > 0
                else self._raise_invalid_root(x, y)
            ),
        }

        operation = operations.get(self.operation)
        if not operation:
            logging.error("Unsupported operation: %s", self.operation)
            raise OperationError(f"Unsupported operation: {self.operation}")

        try:
            return operation(self.operand1, self.operand2)
        except (InvalidOperation, ValueError, ArithmeticError) as error:
            logging.error("Invalid operation: %s", error)
            raise OperationError(f"Invalid operation: {error}")

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal):
        if y == 0:
            raise OperationError("zero root is not defined.")
        if x < 0:
            raise OperationError("Cannot calculate root of a negative number.")
        raise OperationError("Invalid root operation")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Calculation":
        try:
            calc = Calculation(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"]),
            )

            calc.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
            saved_result = Decimal(data["result"])
            if calc.result != saved_result:
                logging.warning(
                    "Calculated result %s does not match saved result %s. Using calculated result.",
                    calc.result,
                    saved_result,
                )
            return calc
        except (KeyError, InvalidOperation, ValueError) as error:
            logging.error("Invalid data for creating Calculation: %s", error)
            raise OperationError(f"Invalid data for creating Calculation: {error}")
    def __str__(self) -> str:
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result} at {self.timestamp.isoformat()}"
    
    def __repr__(self) -> str:

        return (
            f"Calculation(operation={self.operation}, operand1={self.operand1}, operand2={self.operand2}, "
            f"result={self.result}, timestamp={self.timestamp.isoformat()})"
        )
    
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result 
        )
    
    def format_result(self, precision: int = 10) -> str:

        try: 
            return str(self.result.normalize().quantize(
                Decimal('0.' + '0' * precision)
            ).normalize())
        except (InvalidOperation): #pragma: no cover
            raise OperationError(f"Error in formatting result: {str(self.result)}") 