# AGENTS.md

## Purpose

This document provides guidance for AI agents, assistants, and automated contributors interacting with this repository.

## Repository Overview

* Project Type: Python Application
* Primary Language: Python
* Package Manager: pip / uv
* Version Control: Git

## Development Guidelines

1. Preserve existing functionality.
2. Follow project coding standards.
3. Keep changes minimal and focused.
4. Update documentation when making feature changes.
5. Avoid introducing unnecessary dependencies.

## Testing

Before submitting changes:

```bash
pytest
```

or

```bash
python -m pytest
```

## Documentation

* Update README.md when features change.
* Update USER_MANUAL.md for user-facing changes.
* Update CHANGELOG.md for significant releases.

## Security

* Never commit secrets, API keys, or credentials.
* Use environment variables for configuration.
* Follow responsible disclosure practices.

## Commit Message Format

Examples:

```text
feat: add authentication support
fix: resolve upload validation error
docs: update installation instructions
```

## Agent Expectations

* Make reversible changes where possible.
* Explain major modifications clearly.
* Prefer readability and maintainability over complexity.
