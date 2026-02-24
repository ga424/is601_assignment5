from decimal import Decimal
from pathlib import Path
import sys

if __package__ is None or __package__ == "":  # pragma: no cover
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory


def calculator_repl() -> None:
    print("Welcome to the Calculator REPL!")
    print("Type 'exit' to quit.")
    print("Available operations: add, subtract, multiply, divide, power, root")

    try:
        calc = Calculator()
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))
    except KeyboardInterrupt:
        print("\nExiting the Calculator REPL. Goodbye!")
        return
    except EOFError:
        print("\nExiting the Calculator REPL. Goodbye!")
        return
    except Exception as error:
        print(f"An error occurred: {error}")
        return

    print("Calculator initialized. You can start entering operations.")

    while True:
        try:
            command = input("Enter command: ").lower().strip()

            if command == "help":
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

            if command == "exit":
                try:
                    calc.save_history()
                    print("History saved successfully.")
                except Exception as error:
                    print(f"Failed to save history: {error}")
                print("Goodbye!")
                break

            if command == "history":
                history = calc.show_history()
                if not history:
                    print("No calculations performed yet.")
                else:
                    print("\nCalculation History:")
                    for index, line in enumerate(history, 1):
                        print(f"{index}. {line}")
                continue

            if command == "clear":
                calc.clear_history()
                print("Calculation history cleared.")
                continue

            if command == "undo":
                print("Last calculation undone." if calc.undo() else "Nothing to undo.")
                continue

            if command == "redo":
                print("Last undone calculation redone." if calc.redo() else "Nothing to redo.")
                continue

            if command == "save":
                try:
                    calc.save_history()
                    print("History saved successfully.")
                except Exception as error:
                    print(f"Failed to save history: {error}")
                continue

            if command == "load":
                try:
                    calc.load_history()
                    print("History loaded successfully.")
                except Exception as error:
                    print(f"Failed to load history: {error}")
                continue

            if command in ["add", "subtract", "multiply", "divide", "power", "root"]:
                try:
                    operation = OperationFactory.create_operation(command)
                    calc.set_operation(operation)

                    print("\nEnter operands for the operation (or 'cancel' to abort):")
                    operand1_input = input("Operand 1: ").strip()
                    if operand1_input.lower() == "cancel":
                        print("Operation cancelled.")
                        continue

                    operand2_input = input("Operand 2: ").strip()
                    if operand2_input.lower() == "cancel":
                        print("Operation cancelled.")
                        continue

                    result = calc.perform_operation(Decimal(operand1_input), Decimal(operand2_input))
                    if isinstance(result, Decimal):
                        result = result.normalize()
                    print(f"Result: {result}")
                except (ValidationError, OperationError) as error:
                    print(f"Operation failed: {error}")
                except Exception as error:
                    print(f"Unexpected error: {error}")
                continue

            print("Unknown command. Type 'help' for a list of available commands.")

        except KeyboardInterrupt:
            print("\nExiting the Calculator REPL. Goodbye!")
            break
        except EOFError:
            print("\nExiting the Calculator REPL. Goodbye!")
            break


if __name__ == "__main__":  # pragma: no cover
    calculator_repl()
