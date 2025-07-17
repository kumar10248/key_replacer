# Contributing to Key Replacer

Thank you for your interest in contributing to Key Replacer! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python and GUI development

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/key-replacer.git
   cd key-replacer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Run the application in development mode**
   ```bash
   python -m keyreplacer
   ```

## Code Style

We use several tools to maintain code quality:

### Formatting
- **Black** for code formatting
- **isort** for import sorting

Run formatting:
```bash
black keyreplacer
isort keyreplacer
```

### Linting
- **flake8** for style guide enforcement
- **mypy** for type checking

Run linting:
```bash
flake8 keyreplacer
mypy keyreplacer --ignore-missing-imports
```

### Code Guidelines

1. **Follow PEP 8** style guidelines
2. **Use type hints** where possible
3. **Write docstrings** for classes and functions
4. **Keep functions small** and focused
5. **Use meaningful variable names**
6. **Add comments** for complex logic

### Example Code Style

```python
def add_mapping(self, key: str, value: str) -> bool:
    """
    Add a new text expansion mapping.
    
    Args:
        key: The shortcut key to trigger expansion
        value: The text to expand to
        
    Returns:
        True if mapping was added successfully, False otherwise
    """
    if not key or not value:
        return False
    
    # Process the key according to case sensitivity settings
    processed_key = self._process_key(key)
    
    # Validate the mapping
    if not self._validate_mapping(processed_key, value):
        return False
    
    # Store the mapping
    self.mappings[processed_key] = value
    return self._save_mappings()
```

## Testing

We use pytest for testing. Tests are located in the `tests/` directory.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=keyreplacer

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Writing Tests

1. **Test file naming**: `test_*.py`
2. **Test function naming**: `test_*`
3. **Use descriptive test names**
4. **Test both success and failure cases**
5. **Mock external dependencies**

Example test:
```python
def test_add_mapping_success():
    """Test successful addition of a mapping."""
    config = Config()
    result = config.add_mapping("test", "test value")
    
    assert result is True
    assert "test" in config.get_mappings()
    assert config.get_mappings()["test"] == "test value"

def test_add_mapping_empty_key():
    """Test that empty keys are rejected."""
    config = Config()
    result = config.add_mapping("", "test value")
    
    assert result is False
    assert len(config.get_mappings()) == 0
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Run the full test suite**
   ```bash
   pytest
   black keyreplacer
   flake8 keyreplacer
   mypy keyreplacer --ignore-missing-imports
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a pull request**
   - Use a descriptive title
   - Explain what changes you made and why
   - Reference any related issues

### Commit Message Guidelines

Use clear, descriptive commit messages:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

Examples:
```
feat: add import/export functionality for mappings
fix: resolve keyboard listener crash on Linux
docs: update README with installation instructions
test: add tests for configuration management
```

## Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **System information** (OS, Python version, etc.)
5. **Log files** if available
6. **Screenshots** if relevant

Use the bug report template when creating issues.

## Feature Requests

When requesting features:

1. **Describe the feature** clearly
2. **Explain the use case** and benefits
3. **Consider implementation** complexity
4. **Check existing issues** for duplicates

## Development Guidelines

### Architecture

- **keyreplacer/config.py**: Configuration and data management
- **keyreplacer/core.py**: Core text replacement engine
- **keyreplacer/gui.py**: User interface components
- **keyreplacer/main.py**: Application entry point
- **keyreplacer/logging_setup.py**: Logging configuration

### Adding New Features

1. **Design first**: Think about the architecture and user experience
2. **Start small**: Implement the minimal viable version first
3. **Test thoroughly**: Add comprehensive tests
4. **Document**: Update README and help text
5. **Consider platforms**: Ensure cross-platform compatibility

### Platform Considerations

- **Windows**: Handle Windows-specific keyboard APIs
- **macOS**: Consider accessibility permissions
- **Linux**: Support both X11 and Wayland where possible

## Getting Help

- **Documentation**: Check the README and help system
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Ask for feedback in pull requests

## Recognition

Contributors will be recognized in:
- The CHANGELOG.md file
- The About dialog in the application
- The GitHub contributors list

Thank you for contributing to Key Replacer! 🚀
