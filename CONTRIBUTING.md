# Contributing to Homepage

Thank you for your interest in contributing to Homepage! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip

### Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/homepage.git
cd homepage
```

2. Create a virtual environment and install dependencies:
```bash
make install-dev
```

3. Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the code style guidelines

3. Run tests and linters:
```bash
make check
```

4. Commit your changes with descriptive commit messages:
```bash
git commit -m "Add feature: description of your changes"
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions small and focused
- Maximum line length: 100 characters

The project uses these tools for code quality:
- **Black**: Code formatting
- **Ruff**: Fast linting
- **Pylint**: Additional linting
- **Pyright**: Type checking

Run all checks with:
```bash
make check
```

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

Run tests:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Documentation

- Update README.md if adding new features
- Update docstrings for modified functions
- Add examples for new functionality
- Update CHANGELOG.md with your changes

## Pull Request Process

1. Update the documentation with details of changes
2. Ensure all tests pass and code quality checks succeed
3. Update the CHANGELOG.md with your changes
4. Submit a pull request with a clear description of changes

### PR Guidelines

- Keep PRs focused on a single feature or fix
- Write clear, descriptive PR titles
- Include context and motivation in PR description
- Link related issues in the PR description
- Respond to review feedback promptly

## Commit Message Guidelines

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(search): add DuckDuckGo search provider
fix(cache): resolve TTL expiration issue
docs(readme): update installation instructions
```

## Project Structure

```
homepage/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── metrics.py          # Metrics collection
├── cli.py              # Command-line interface
├── templates/          # HTML templates
├── static/             # Static assets
├── tests/              # Test files
└── docs/               # Documentation
```

## Adding New Features

### New Configuration Options

1. Add to `config.py` with environment variable support
2. Document in README.md
3. Add validation if needed
4. Update tests

### New Endpoints

1. Add route in `app.py`
2. Add tests in `tests/test_app.py`
3. Document in README.md or API docs
4. Update health check if critical

### New Dependencies

1. Add to `requirements.txt` (production) or `requirements-dev.txt` (development)
2. Update `pyproject.toml` if needed
3. Update Dockerfile if affects Docker build
4. Document why dependency is needed

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, etc.)
- Relevant logs or screenshots

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Examples or mockups (if applicable)

## Code Review Process

Maintainers will review your PR and may:
- Request changes
- Ask questions
- Suggest improvements
- Approve and merge

Be patient and responsive to feedback.

## Getting Help

- Check existing issues and documentation
- Ask questions in issues or discussions
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing! 🎉
