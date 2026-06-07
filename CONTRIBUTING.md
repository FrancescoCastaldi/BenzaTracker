# Contributing to BenzaTracker

Thanks for your interest! We welcome contributions of all kinds.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Commit Convention](#commit-convention)
- [Pull Request Workflow](#pull-request-workflow)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Ways to Contribute

- **Report a bug** — open a [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml)
- **Suggest a feature** — open a [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml)
- **Fix an issue** — check the [open issues](https://github.com/FrancescoCastaldi/BenzaTracker/issues)
- **Improve documentation** — typos, clarifications, translations
- **Review pull requests** — feedback is always appreciated

## Development Setup

### 1. Fork and clone

```bash
git clone https://github.com/YOUR_USERNAME/BenzaTracker.git
cd BenzaTracker
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Install with dev dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode plus dev tools (pytest, ruff, mypy, pre-commit).

### 4. Install pre-commit hooks (recommended)

```bash
pre-commit install
```

This runs ruff, mypy, and formatting checks automatically before every commit.

## Coding Guidelines

- **Python 3.10+** — we use `str.removeprefix`, `str.removesuffix`, `match`/`case`
- **Type hints** — all functions must have typed signatures; run `mypy` before pushing
- **Linting** — `ruff` with rules `E, F, W, I, UP, B, C4, SIM` (line length 100)
- **Imports** — use absolute imports; group stdlib → third-party → local
- **Null safety** — prefer `Optional[T]` over implicit `None`; use `is` for `None` checks
- **Error handling** — raise specific exceptions; avoid bare `except:`

Run the linter before committing:

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
```

## Commit Convention

We use **Conventional Commits** (enforced by pre-commit):

| Prefix     | Usage                             |
|------------|-----------------------------------|
| `feat:`    | A new feature                     |
| `fix:`     | A bug fix                         |
| `docs:`    | Documentation only                |
| `refactor:`| Code change that neither fixes nor adds a feature |
| `test:`    | Adding or correcting tests        |
| `chore:`   | Build process, CI, tooling        |
| `style:`   | Formatting, missing semicolons (no production change) |

Format:

```
<type>: <short description>

[optional body — explain why, not what]

[optional footer — e.g., Closes #123]
```

Examples:

```
feat: add SQLite store with CRUD operations
fix: handle empty refuel list in KPI computation
docs: clarify LAUNCH_GUIDE env var section
refactor: unify store protocol between JSON and SQLite
```

## Pull Request Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
2. **Make your changes** — keep commits small and focused
3. **Run tests** — ensure they pass:
   ```bash
   pytest -v --tb=short
   ```
4. **Push and open a PR** against `main`
5. **Ensure CI passes** — the GitHub Actions workflow runs tests on Python 3.10–3.12
6. **Request review** — a maintainer will review within a few days

### PR checklist before submitting

- [ ] Code follows style guidelines (ruff, mypy)
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] Changelog entry added under `[Unreleased]`
- [ ] No breaking changes without discussion

## Testing

We use `pytest` with `pytest-cov` for coverage.

```bash
pytest -v --tb=short         # run all tests
pytest tests/test_kpi.py     # run a single file
pytest -k "sqlite"           # run tests matching "sqlite"
pytest --cov=benzatracker    # with coverage report
```

Tests live in `tests/` and should never require network access or a display server.

## Project Structure

```
src/benzatracker/          # main package (src/ layout)
tests/                     # test suite
.github/workflows/         # CI pipeline
docs/                      # assets (logo, etc.)
```

For a detailed tree, see the [README](README.md#project-structure).

---

*First time contributing to open source? Check out*
*[How to Contribute to Open Source](https://opensource.guide/how-to-contribute/).*
