# MICC Modernization Plan

## Background & Motivation
MICC is a legacy mathematical software project originally written in Python 2 and C++. The current C++ implementation relies on the deprecated Python 2 C API (`<Python.h>`) as well as a JSON subprocess parsing mechanism for inter-language communication. The goal of this modernization effort is to transition the codebase to Python 3, replace the legacy C++ bindings with **Pybind11**, and decouple the core application logic from the CLI to prepare for a future **PyQt6/PySide6** GUI.

## Scope & Impact
The modernization will touch almost every part of the codebase:
- **Python Code (`micc/*.py`)**: Transition to Python 3 syntax and libraries.
- **C++ Code (`micc/util-dfs.cpp`, `micc/dfs2.cpp`)**: Complete replacement of the Python 2 C API logic with Pybind11 bindings. 
- **Build System (`setup.py`, `build.sh`)**: Update to compile Pybind11 extensions.
- **Architecture (`micc/cli.py`)**: Extraction of core logic to support a headless API for the upcoming PyQt6 GUI.
- **Testing (`micc/tests/`)**: Upgrade test runners to be compatible with Python 3.

## Proposed Solution

### 1. Python 3 Porting
- Update syntax: Replace `print` with `print()`, `raw_input()` with `input()`, and `xrange()` with `range()`.
- Update dictionary iterators: Replace `iteritems()` with `items()`.
- Handle legacy types and division: Ensure integer division (`//` vs `/`) is correct, and replace references to `sys.maxint` with `sys.maxsize`.
- Upgrade dependencies in `setup.py` and `requirements.txt` (e.g., migrating from `nose` to `pytest`, as `nose` is unmaintained).

### 2. Pybind11 C++ Bindings
- **Clean C++ Sources**: Remove all `<Python.h>` references and legacy C API boilerplates (`PyInt_AsLong`, `PyDict_Next`, etc.) from `util-dfs.cpp`.
- **Create Pybind11 Module**: Expose the core DFS algorithms (`cdfs` and `loop_dfs`) via a new Pybind11 module (e.g., `_micc_dfs`). This module will natively handle the conversion between C++ `std::map`/`std::vector` and Python `dict`/`list`.
- **Integrate into Python**: Refactor `micc/cgraph.py` and `micc/graph.py` to import and call `_micc_dfs` directly, entirely removing the `subprocess` JSON passing and `intermed.json` file writes.

### 3. GUI Groundwork (PyQt6 Preparation)
- Extract the state management (e.g., `curve`, `ladder`, `perms`) and computation logic out of the `CLI` class in `micc/cli.py` into a new, reusable API class (e.g., `MiccCore`).
- Refactor the `CLI` class to act merely as a thin input/output wrapper around `MiccCore`.
- This ensures the future PyQt6 application can instantiate `MiccCore` and interact with the engine without being tangled in terminal I/O logic.

## Alternatives Considered
- **Cython**: While traces of Cython exist in the build scripts, Pybind11 was selected for its minimal boilerplate, pure C++ approach, and modern standard status.
- **JSON Subprocess**: The existing `dfs2` / `util-dfs` executable subprocess approach has performance overhead from string serialization/deserialization. A native module is faster and cleaner.
- **Tkinter/Web UI**: Rejected in favor of the user's preference for PyQt6/PySide6 to build a powerful desktop application.

## Phased Implementation Plan

### Phase 1: Python 3 Syntax Migration
- Run automated `2to3` or manually update all `.py` files to Python 3 syntax.
- Update `setup.py` dependencies.
- Fix tests to run correctly under Python 3 (migrate to `pytest`).

### Phase 2: Pybind11 Integration
- Install `pybind11`.
- Strip legacy Python 2 C API code from `micc/util-dfs.cpp`.
- Write the `PYBIND11_MODULE` block to expose the `cdfs` function.
- Update `setup.py` to build the Pybind11 extension using `pybind11.setup_helpers.Pybind11Extension`.

### Phase 3: Wiring Python to C++
- Modify `micc/graph.py` and `micc/cgraph.py` to import the new `_micc_dfs` module.
- Ensure the types passed from Python strictly match the expected Pybind11 signatures.
- Run the test suite to verify that the C++ DFS algorithms yield identical results to the legacy implementation.

### Phase 4: CLI Decoupling
- Refactor `micc/cli.py` into two distinct components: `MiccCore` (logic) and `CLI` (terminal UI).
- Document the `MiccCore` methods to ease the upcoming PyQt6 implementation.

### Phase 5: Advanced Visualization & Interactive Analysis
- **Relational Mapping**: Build interactive tools (likely using libraries like `networkx` and `matplotlib` or integrated into the PyQt6 canvas) to visualize the curve complex connections.
- **Beyond Basics**: Ensure the visualizer can handle complex, high-intersection patterns and higher-genus surfaces that are difficult to interpret through raw matrices or paths.
- **Interactive Exploration**: Allow users to interact with nodes and edges in the curve complex to reveal underlying mathematical properties (genus, distance, etc.) visually.

## Verification
- **Test Suite**: Ensure all tests in `micc/tests/` pass with the new Pybind11 extension under Python 3.
- **Manual CLI Testing**: Run standard workflows (e.g., entering ladders, calculating genus, and distance) to verify end-to-end functionality.
- **Performance Profiling**: Ensure the Pybind11 native calls perform equivalently or faster than the old JSON subprocess calls.
- **Visualization Quality**: Verify that the new visualization tools correctly represent the mathematical relationships in the curve complex for complex edge cases.

## Migration & Rollback
- All modernization work will be conducted on a feature branch (e.g., `feature/modernization-py3`).
- If the Pybind11 integration introduces blocking issues, the team can temporarily fallback to compiling the C++ as an executable and communicating via the existing JSON subprocess (`intermed.json`), while the binding issues are resolved.
