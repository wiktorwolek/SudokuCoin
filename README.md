# SudokuCoin

SudokuCoin is an experimental, educational Python project that implements a simple blockchain / cryptocurrency concept using Sudoku-based hashing / proof ideas.
The repository contains several Python modules for running a single-node coin, a P2P node, a wallet, and utilities for hashing/validation using Sudoku-based logic.

**Not for production use.** This project is intended for learning, experimentation and prototyping. See the source files in the repository for implementation details.

---

## Features

* A minimal Python implementation of a coin / blockchain (single-node and node modules)
* Sudoku-based hashing / puzzle approach (in `SudokuHasher.py`)
* Simple P2P / networking utilities (`P2P.py`, `HttpClient.py`)
* Wallet and transaction-related helpers (`Wallet.py`)
* Test and helper scripts / batch files for quick runs on Windows

---

## Requirements

* Python 3.8+
* A few common Python libraries may be required depending on which scripts you run (requests, flask, or similar) — check the top of each script for imports. If you run into `ModuleNotFoundError`, install the missing package via `pip`.

---

## Quick start

1. Clone the repository:

```bash
git clone https://github.com/wiktorwolek/SudokuCoin.git
cd SudokuCoin
```

2. Inspect the scripts to decide which component to run. Typical entry points:

* Run the main coin script (single-node / demonstration):

```bash
python SudoCoin.py
```

* Run a node implementation:

```bash
python SudokuCoinNode.py
```

* Interact with the wallet:

```bash
python Wallet.py
```

* Run tests or helpers:

```bash
python test.py
# or on Windows:
test.bat
```

---

## How it works

### Sudoku-based Hashing

Instead of using SHA-256 or another standard cryptographic hash, SudokuCoin explores an **alternative hashing mechanism inspired by Sudoku puzzles**:

1. **Grid initialization**: Transaction data or block data is transformed into numbers that fill a Sudoku-like grid.
2. **Constraint solving**: The grid must satisfy Sudoku constraints (unique numbers per row, column, and subgrid).
3. **Hash derivation**: The filled/solved Sudoku grid is then serialized into a numeric or string representation that serves as the “hash” of the data.
4. **Difficulty adjustment**: The puzzle’s constraints (e.g., number of prefilled cells) can be tuned to make solving more or less difficult, mimicking proof-of-work difficulty in blockchains.

This approach is **not cryptographically secure** but is meant as an educational demonstration of how alternative puzzle-based proofs could be integrated into blockchain concepts.

---

## Contributing

This is an experimental/personal project — contributions are welcome. If you plan to contribute:

1. Fork the repository.
2. Create a branch for your changes.
3. Open a pull request with a clear description of what you changed and why.

---

## License

This project is licensed under the [MIT License](LICENSE).  
You are free to use, modify, and distribute it under the terms of this license.


---

## Disclaimer

This project is for learning and experimentation only. It is not secure, audited, or suitable for any real monetary use.
