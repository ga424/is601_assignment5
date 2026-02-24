# IS601 Assignment 5 — NotebookLM Study Guide

## 1) What this project teaches
This calculator project demonstrates how to design a clean Python application using object-oriented principles, multiple design patterns, robust error handling, file persistence, and high-confidence testing.

Core outcomes:
- Build extensible arithmetic logic
- Separate concerns (input validation, operations, persistence, UI loop)
- Use patterns to keep code scalable and maintainable
- Validate behavior with full automated testing

---

## 2) Architecture at a glance
- `app/calculator_repl.py`: interactive CLI loop (user commands)
- `app/calculator.py`: orchestrator/service layer (business workflow)
- `app/operations.py`: operation strategy classes + factory
- `app/calculation.py`: calculation entity/model + serialization helpers
- `app/history.py`: observers for logging and autosave behavior
- `app/calculator_memento.py`: state snapshots for undo/redo
- `app/calculator_config.py`: environment/config management and validation
- `app/input_validators.py`: input constraints and Decimal conversion
- `app/exceptions.py`: custom exception hierarchy

Flow summary:
1. REPL reads command + operands.
2. Factory creates operation strategy.
3. Calculator validates inputs and executes operation.
4. Calculation is recorded in history.
5. Observers are notified (logging/autosave).
6. History can be saved/loaded; undo/redo uses mementos.

---

## 3) OOP concepts used
### Encapsulation
`Calculator` manages internal state (`history`, `undo_stack`, `redo_stack`) through methods instead of exposing mutation.

### Abstraction
`Operation` is an abstract base class defining the operation contract (`execute`).

### Polymorphism
`Addition`, `Subtraction`, `Division`, `Power`, etc. implement the same `execute` interface with different behavior.

### Composition over inheritance
`Calculator` composes strategies, observers, and mementos rather than relying on deep inheritance trees.

---

## 4) Design patterns mapped to code
### Strategy Pattern
- **Where**: `Operation` + concrete operation classes
- **Why**: swap calculation behavior at runtime (`set_operation`)

### Factory Pattern
- **Where**: `OperationFactory`
- **Why**: central operation creation by command name; avoids condition-heavy construction in REPL

### Observer Pattern
- **Where**: `HistoryObserver`, `LoggingObserver`, `AutoSaveObserver`
- **Why**: react to new calculations without tightly coupling side effects to core computation

### Memento Pattern
- **Where**: `CalculatorMemento`
- **Why**: capture/restore history snapshots for undo/redo safely

---

## 5) Data modeling and precision
- `Decimal` is used to avoid floating-point inaccuracies in arithmetic.
- `@dataclass` simplifies model classes and improves readability.
- `Calculation` supports `to_dict`/`from_dict` for reliable persistence.

Important idea:
- Domain objects should be serializable and reconstructable to support persistence and replay of state.

---

## 6) Error handling strategy
Custom hierarchy:
- `CalculatorError` (base)
- `ValidationError`
- `OperationError`
- `ConfigurationError`

Why this matters:
- You get precise failures by layer (validation vs operation vs configuration).
- The REPL can show user-friendly messages while preserving structured internal exceptions.

---

## 7) Configuration and environment design
`CalculatorConfig` loads values from defaults and environment variables, then validates constraints.

Examples:
- max history size
- precision
- max input value
- base/log/history paths

Key principle:
- Centralized config + validation prevents scattered “magic values” and runtime surprises.

---

## 8) Persistence and state management
- History is stored in CSV (via pandas).
- Save/load transforms `Calculation` objects to/from dictionaries.
- Undo/redo uses memento snapshots (copy history state before mutation).

State safety concepts:
- Before each new calculation, push current state to `undo_stack`.
- Any new operation clears `redo_stack`.

---

## 9) Testing strategy used in this project
The tests emphasize:
- Unit tests for each module
- Positive + negative paths
- Branch/error-path coverage
- Monkeypatching for filesystem, environment, and REPL interaction

Why this is strong:
- It validates behavior, not just happy paths.
- It catches regressions in command flow, config parsing, and serialization.

---

## 10) High-value discussion points for exams/interviews
1. Why combine Strategy + Factory here instead of `if/elif` for operations?
2. How does Observer reduce coupling in logging/autosave?
3. Why is Memento a better fit than manually undoing operations one-by-one?
4. Why are Decimals preferable for this domain?
5. What are trade-offs of CSV persistence vs database storage?
6. Why wrap lower-level exceptions into domain-specific exceptions?
7. What bugs are prevented by environment/config validation at startup?
8. How does test isolation with monkeypatch improve reliability?
9. What would change if this moved from REPL to REST API?
10. Which components are easiest to extend and why?

---

## 11) Quick extension ideas (for deeper mastery)
- Add modulo/logarithm operations via `OperationFactory.register_operation`
- Add JSON history backend alongside CSV
- Add command aliases and command parsing abstraction
- Add structured logging and request/session IDs
- Add integration tests for complete REPL sessions

---

## 12) 60-second summary
This codebase is a practical example of clean architecture in Python: a CLI-driven calculator built with Strategy/Factory/Observer/Memento patterns, precise decimal arithmetic, robust validation and exception handling, persistent history, undo/redo state management, and comprehensive automated testing.
