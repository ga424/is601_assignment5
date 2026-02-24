from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict

from app.exceptions import OperationError

@dataclass
class Calculation:

    operation: str  #placeholder for operation type, e.g., 'add', 'subtract', 'multiply', 'divide'
    operand1: Decimal #placeholder for the first operand
    operand2: Decimal #placeholder for the second operand

    result: Decimal = field(init=False) #result will be calculated based on the operation and operands
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now) # system timestamp of when the calculation was performed

    def __post_init__(self): # This method is called after the dataclass has been initialized. It performs the calculation based on the operation and operands.
        
        self.result = self.calculate()
    
    def calculate(self) -> Decimal:
        operations = {
            'Addition': lambda x, y: x + y,
            'Subtraction': lambda x, y: x - y,
            'Multiplication': lambda x, y: x * y,
            'Division': lambda x, y: x / y,
            'Power': lambda x, y: x ** y,
            'Root': lambda x, y: (
                Decimal(pow(float(x), 1/float(y)))
                if x >= 0 and y > 0 else
                self.raise_invalid_root(x, y)
            )
        }

        op = operations.get(self.operation)
        
        # If the operation is not supported (i.e., not found in the operations dictionary), log an error and raise an OperationError to indicate that the requested operation is invalid.
        if not op:
            logging.error(f"Unsupported operation: {self.operation}")
            raise OperationError(f"Unsupported operation: {self.operation}")
        
        try: 
            # Perform the calculation using the appropriate operation function. The lambda functions defined in the operations dictionary will handle the actual computation based on the provided operands.
            return op(self.operand1, self.operand2)
        
        # Handle specific cases for root operation to provide more informative error messages, especially for invalid inputs.
        except (InvalidOperation, ValueError, ArithmeticError) as e:
            logging.error(f"Invalid operation: {e}")
            raise OperationError(f"Invalid operation: {str(e)}")
        

        @staticmethod
        def _raise_div_zero(): #pragma: no cover
            logging.error("Division by zero attempted.")
            raise OperationError("Division by zero is not allowed.")
        
        @staticmethod
        def _raise_neg_power(): #pragma: no cover
            raise OperationError("Negative exponent is not allowed for Power operation.")
        
        @staticmethod
        def _raise_invalid_root(x: Decimal, y: Decimal): #pragma: no cover
            if y == 0:
                raise OperationError("zero root is not defined.")
            if x < 0:
                raise OperationError("Cannot calculate root of a negative number.")
            
            raise OperationError("Invalid root operation")
        
        def to_dict(self) -> Dict[str, Any]: # This method converts the Calculation instance into a dictionary format, which can be useful for serialization or for returning structured data in an API response.
            return {
                "operation": self.operation,
                "operand1": str(self.operand1),  # Convert Decimal to string for better readability
                "operand2": str(self.operand2),  # Convert Decimal to string for better readability
                "result": str(self.result),      # Convert Decimal to string for better readability
                "timestamp": self.timestamp.isoformat()  # Convert datetime to ISO format string
            }
        
        @staticmethod
        def from_dict(data: Dict[str, Any]) -> 'Calculation': 
            # This static method creates a Calculation instance from a dictionary.
            # It expects the dictionary to contain the keys 'operation', 'operand1', and 'operand2', and it converts the operand values from strings to Decimal before initializing the Calculation instance.

            try: 
                calc = Calculation(
                    operation=data['operation'],
                    operand1=Decimal(data['operand1']),
                    operand2=Decimal(data['operand2'])
                )

                # Set the timestamp form the provided saved data with current time rather than instance creation time
                calc.timestamp = datetime.datetime.fromisoformat(data['timestamp'])

                saved_result = Decimal(data['result'])
                if calc.result != saved_result:
                    # if the calculated result does not match the saved result, log a warning and use the calculated result instead. 
                    # This can happen if there were changes in the calculation logic or if there was an error in the saved data.
                    logging.warning(f"Calculated result {calc.result} does not match saved result {saved_result}. Using calculated result.")
                
                return calc

            except (KeyError, InvalidOperation, ValueError) as e:
                logging.error(f"Invalid data for creating Calculation: {str(e)}")
                raise OperationError(f"Invalid data for creating Calculation: {str(e)}" )
        
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
                self.result == other.result and
                self.timestamp == other.timestamp
            )
        
        def format_result(self, precision: int = 10) -> str:

            try: 
                return str(self.result.normalize().quantize(
                    Decimal('0.' + '0' * precision)
                ).normalize())
            except (InvalidOperation): #pragma: no cover
                raise OperationError(f"Error in formatting result: {str(self.result)}")   
            

