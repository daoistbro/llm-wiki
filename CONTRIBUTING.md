# Contributing to LLM Wiki

Thank you for your interest in contributing to LLM Wiki! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/daoistbro/llm-wiki.git
cd llm-wiki

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
black src/
```

## Development Workflow

1. **Fork the repository** on GitHub
2. **Create a branch** for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines
4. **Write tests** for new functionality
5. **Run tests** to ensure everything passes
   ```bash
   pytest
   ```
6. **Commit your changes** with a clear message
   ```bash
   git commit -m "Add: feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request** on GitHub

## Code Style

We use:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting

Run the formatters before committing:
```bash
black src/ tests/
ruff check --fix src/ tests/
```

## Testing

- Write tests for new features in `tests/`
- Ensure all tests pass before submitting a PR
- Aim for good test coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=llm_wiki --cov-report=html

# Run specific test
pytest tests/test_core.py::TestLLMWiki::test_init_creates_directories
```

## Commit Messages

Follow conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for custom page types
fix: resolve issue with hash collision detection
docs: update README with new examples
```

## Pull Request Guidelines

- Describe what your PR does
- Link to related issues
- Include screenshots if applicable
- Ensure all CI checks pass
- Request review from maintainers

## Reporting Issues

When reporting bugs, please include:
- Python version
- OS version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/stack traces

## Feature Requests

For feature requests:
- Describe the use case
- Explain why it's needed
- Suggest possible implementations
- Consider if it fits the project's scope

## Questions

Feel free to open a discussion for questions about:
- How to use the library
- Design decisions
- Best practices

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Be respectful and constructive. We're all here to build something great together!
