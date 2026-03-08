# Assignments for CS146S: The Modern Software Developer

This is the home of the assignments for [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University fall 2025.

## Repo Setup
These steps work with Python 3.12.

1. Install Anaconda
   - Download and install: [Anaconda Individual Edition](https://www.anaconda.com/download)
   - Open a new terminal so `conda` is on your `PATH`.

2. Create and activate a Conda environment (Python 3.12)
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

3. Install Poetry
   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

4. Install project dependencies with Poetry (inside the activated Conda env)
   From the repository root:
   ```bash
   poetry install --no-interaction
   ```

## Makefile Python Environment

The top-level `Makefile` uses the current shell's Python by default:

```make
PY ?= python
```

Recommended usage:

1. Activate the environment you want to use first.
   ```bash
   conda activate cs146s
   ```
2. Run `make` targets normally.
   ```bash
   make w1-k-shot
   make w2-test
   ```

If you need a specific interpreter for one command, override `PY` explicitly:

```bash
make PY=python3 w1-k-shot
make PY=/path/to/python w2-test
```

This keeps the default configuration simple and avoids hardcoding machine-specific Python paths in the repository.
