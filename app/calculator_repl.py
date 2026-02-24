from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.operations import Operation

def calculator_repl():

    print("Welcome to the Calculator REPL!")
    print("Type 'exit' to quit.")
    print("Available operations: add, subtract, multiply, divide, power, root")

    while True:
        try:

            calculator = Calculator()  # Create an instance of the Calculator class to perform calculations.
            
            calc.add_observer(HistoryObserver())  # Add a HistoryObserver to the calculator instance to track the history of calculations performed during the REPL session.
            calc.add_observer(AutoSaveObserver(calc))  # Add an AutoSaveObserver to the calculator instance to automatically save the history of calculations after each operation.

            print("Calculator initialized. You can start entering operations.")
            
            while True:
                
                command = input("Enter command: ").lower().strip()
                
                if command == 'help':
                   # Display available commands
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root - Perform calculations")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    print("Exiting the Calculator REPL. Goodbye!")

                    try:
                        calc.save_history()  # Attempt to save the calculation history before exiting the REPL.
                        print ("History saved successfully.")
                    
                    except Exception as e:
                        print(f"Failed to save history: {e}")
                    print("Goodbye!")
                    break
                
                if command == 'history':
                    history = calc.get_history()  # Retrieve the calculation history from the calculator instance.
                    if not history:
                        print("No calculations performed yet.")
                    else:
                        print("\nCalculation History:")
                        for idx, entry in enumerate(history, 1):
                            print(f"{idx}. {entry.operation} {entry.operand1} {entry.operand2} = {entry.result} (at {entry.timestamp})")
                    continue
                if command == 'clear':
                    calc.clear_history()  # Clear the calculation history in the calculator instance.
                    print("Calculation history cleared.")
                    continue
                if command == 'undo':
                    try:
                        calc.undo()  # Attempt to undo the last calculation performed in the calculator instance.
                        print("Last calculation undone.")
                    except Exception as e:
                        print(f"Failed to undo: {e}")
                    continue
                if command == 'redo':
                    try:
                        calc.redo()  # Attempt to redo the last undone calculation in the calculator instance.
                        print("Last undone calculation redone.")
                    except Exception as e:
                        print(f"Failed to redo: {e}")
                    continue
                if command == 'save':
                    try:
                        calc.save_history()  # Attempt to save the calculation history to a file using the calculator instance.
                        print("History saved successfully.")
                    except Exception as e:
                        print(f"Failed to save history: {e}")
                    continue
                if command == 'load':
                    try:
                        calc.load_history()  # Attempt to load the calculation history from a file using the calculator instance.
                        print("History loaded successfully.")
                    except Exception as e:
                        print(f"Failed to load history: {e}")
                    continue
                
                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root']:
                    try:
                        print("\nEnter operands for the operation (or 'cancel' to abort): ")

                        if (operand1_input := input("Operand 1: ").strip().lower()) == 'cancel':
                            print("Operation cancelled.")
                            continue
                        operand1 = Decimal(input("Enter first operand: ").strip())  # Prompt the user to enter the first operand and convert it to a Decimal type for accurate calculations.
                        
                        if (operand2_input := input("Operand 2: ").strip().lower()) == 'cancel':
                            print("Operation cancelled.")
                            continue

                        result = calc.perform_operation(command, operand1, operand2)  # Perform the specified operation using the calculator instance and store the result.
                        
                        if isinstance(result, Decimal):
                            result = result.normalize()
                        
                        print(f"Result: {result}")  # Display the result of the calculation to the user.
                    
                    except (ValidationError, OperationError) as e:
                        print("Invalid input format. Please enter numeric values for operands.")
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                    
                    continue
                
                print ("Unknown command. Type 'help' for a list of available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting the Calculator REPL. Goodbye!")
            break
        except EOFError:
            print("\nExiting the Calculator REPL. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    calculator_repl()

            