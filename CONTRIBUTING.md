# Contributing to AI-Powered Expense Tracker

Thank you for your interest in contributing to this project! We welcome contributions from the community. This guide outlines the process for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

By participating in this project, you agree to:
- Be respectful and inclusive in all interactions
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitLab
2. Clone your fork locally:
   ```bash
   git clone https://code.swecha.org/your-username/expense-tracker.git
   cd expense-tracker
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://code.swecha.org/Abdullah_285/expense-tracker.git
   ```

## Development Setup

### Prerequisites

- Python 3.10+ (Python 3.14+ recommended)
- pip (Python package manager)
- (Optional) Ollama for local AI features

### Installation

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy environment template
cp .env.example .env
```

### Running Locally

```bash
streamlit run app.py
```

The app will be available at **http://localhost:8501**

## Project Structure

```
expense-tracker/
├── app.py                 # Main entry point
├── database/              # Data layer (SQLite + SQLAlchemy)
│   ├── db.py
│   ├── models.py
│   └── repository.py
├── pages/                 # Streamlit UI pages
│   ├── dashboard.py
│   ├── expenses.py
│   ├── reports.py
│   ├── ai_assistant.py
│   └── settings.py
├── services/              # Business logic
│   ├── ai_service.py
│   ├── analytics_service.py
│   └── provider_services/
├── utils/                 # Utilities
│   ├── charts.py
│   ├── helpers.py
│   └── receipt_parser.py
├── tests/                 # Test suite
└── data/                  # Runtime data (gitignored)
```

## Coding Standards

### Python Style

- Follow **PEP 8** guidelines
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters**
- Use **type hints** for function signatures
- Use **docstrings** for all public functions and classes

### Naming Conventions

- `snake_case` for variables, functions, and methods
- `PascalCase` for classes
- `UPPER_CASE` for constants
- `_leading_underscore` for private/internal methods

### Code Quality

- Write clean, readable, and maintainable code
- Avoid duplicate code — extract reusable functions
- Handle errors gracefully with try/except blocks
- Use logging instead of print statements
- Keep functions focused on a single responsibility

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_database.py -v
pytest tests/test_ai_service.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### Writing Tests

- All new features must include unit tests
- Use pytest fixtures for test data
- Tests should be independent and repeatable
- Mock external services (AI APIs) in tests
- Test both success and error scenarios

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Write or update tests** as needed

4. **Run all tests** to ensure nothing is broken:
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add new feature description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Merge Request** on GitLab targeting `main`

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks

### Merge Request Checklist

- [ ] Code follows project coding standards
- [ ] All tests pass
- [ ] New features include tests
- [ ] Documentation is updated (if needed)
- [ ] Changes are backward compatible
- [ ] No sensitive data (API keys, secrets) is exposed

## Reporting Issues

When reporting a bug, please include:

1. **Description** — What happened vs what was expected
2. **Steps to reproduce** — Minimal, complete steps
3. **Environment** — OS, Python version, relevant configurations
4. **Logs/Screenshots** — If applicable
5. **Possible fix** — If you have a suggestion

## Feature Requests

We welcome feature requests! Please:

1. Check existing issues to avoid duplicates
2. Describe the feature clearly and the problem it solves
3. Explain how it would benefit the project
4. If possible, outline a proposed implementation

---

Thank you for contributing! 🚀
