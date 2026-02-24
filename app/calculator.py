from decimal import Decimal
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation

Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]

class Calculator: 
    
    def __init__(self, config: Optional[CalculatorConfig] = None):
        if config is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        os.makedirs(self.config.log_dir, exist_ok=True)

        self._setup_logging()

        self.observers: List[HistoryObserver] = []

        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        self._setup_directories()

        try: 
            self.load_history()
        except Exception as e:
            logging.error(f"Failed to load existing history: {e}")
        
        logging.info("Calculator initialized with configuration: %s", self.config )

    def _setup_logging(self)-> None:

        try: 
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()

            logging.basicConfig(
                filename=str(log_file), 
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True
            )
            logging.info("Logging initialized. Log file: %s", log_file)
        except Exception as e:
            print(f"Failed to set up logging: {e}")
            raise

    def _setup_directories(self) -> None:
        self.config.history_dir.mkdir(parents=True, exist_ok=True)
    
    def add_observer(self, observer: HistoryObserver) -> None:
        self.observers.append(observer)
        logging.info(f"Observer added: {observer.__class__.__name__}")
    
    def remove_observer(self, observer: HistoryObserver) -> None:
        if observer in self.observers:
            self.observers.remove(observer)
            logging.info(f"Observer removed: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        for observer in self.observers:
            observer.update(calculation)    
    
    def set_operation(self, operation: Operation) -> None:
        self.operation_strategy = operation
        logging.info(f"Operation strategy set to: {operation.__class__.__name__}")
    
    def perform_operation(self, a: Union[str, Number], b: Union[str, Number]) -> CalculationResult:

        if not self.operation_strategy:
            logging.error("No operation strategy set.")
            raise OperationError("No operation strategy set.")
        try:

            # Validate inputs and perform the operation using the current strategy. 
            # The validated inputs are converted to Decimal for consistent precision in calculations. 
            # The result of the operation is stored in a Calculation instance, which is then added to the history and observers are notified of the new calculation.
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)
            
            result = self.operation_strategy.execute(validated_a, validated_b)

            calculation = Calculation(
                operation = str(self.operation_strategy), 
                operand1 = validated_a,
                operand2 = validated_b,
                result = result
            ) 

            # Save the current state before performing the operation to enable undo functionality.
            self.undo_stack.append(CalculatorMemento(self.history.copy()))

            # Clear the redo stack whenever a new operation is performed, as the redo history is no longer valid after a new operation.
            self.redo_stack.clear()

            # Append the new calculation to the history 
            self.history.append(calculation)
            
            if len(self.history) > self.config.max_history:
                removed_calculation = self.history.pop(0)
                logging.info(f"History limit exceeded. Removed oldest calculation: {removed_calculation}"  )
            
            self.notify_observers(calculation)
            
            return result
        except ValidationError as e:
            logging.error(f"Input validation error: {e}")
            raise OperationError(f"Input validation error: {str(e)}")
        except Exception as e:
            logging.error(f"Operation error: {e}")
            raise OperationError(f"Operation error: {str(e)}")
    
    def save_history(self) -> None:
        try: 

            self.config.history_dir.mkdir(parents=True, exist_ok=True)
            history_data.append({
                'operation': calc.operation,
                'operand1': str(calc.operand1),
                'operand2': str(calc.operand2),
                'result': str(calc.result),
                'timestamp': calc.timestamp.isoformat()
            })

            if history_data: 
                
                df = pd.DataFrame(history_data)

                df.to_csv(self.config.history_file, index=False)
                logging.info(f"History saved to {self.config.history_file}")
            
            else: 
                pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']).to_csv(self.config.history_file, index=False)
                logging.info(f"History file created: {self.config.history_file}")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")
            raise OperationError(f"Failed to save history: {str(e)}")
        
    def load_history(self) -> None:
        try: 
            if self.config.history_file.exists():
                df = pd.read_csv(self.config.history_file)

                if not df.empty: 
                    self.history = [
                        Calculation.from_dict({ 
                            'operation': row['operation'], 
                            'operand1': row['operand1'], 
                            'operand2': row['operand2'], 
                            'result': row['result'], 
                            'timestamp': row['timestamp'] 
                        })
                        for _, row in df.iterrows()
                    ]
                    logging.info(f"History loaded from {self.config.history_file}. Total calculations: {len(self.history)}")
                else:
                    logging.info(f"History file is empty: {self.config.history_file}")
            else:
                logging.info(f"History file does not exist: {self.config.history_file}")
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            raise OperationError(f"Failed to load history: {str(e)}")
        
    def get_history_dataframe(self) -> pd.DataFrame:
        history_data = []
        
        for calc in self.history:
            history_data.append({
                "operation": calc.operation,
                "operand1": str(calc.operand1),  # Convert Decimal to string for better readability
                "operand2": str(calc.operand2),  # Convert Decimal to string for better readability
                "result": str(calc.result),      # Convert Decimal to string for better readability
                "timestamp": calc.timestamp.isoformat()  # Convert datetime to ISO format string
            })
        return pd.DataFrame(history_data)
    
    def show_history(self) -> None:
        return [
            f"{calc.operation}({calc.operand1}, {calc.operand2}) = {calc.result} at {calc.timestamp.isoformat()}"
            for calc in self.history
        ]

    def clear_history(self) -> None:
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("History cleared.")
    
    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        memento = self.undo_stack.pop()
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True
    
    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        memento = self.redo_stack.pop()
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True
    