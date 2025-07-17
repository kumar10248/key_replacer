# Makefile for Key Replacer development

.PHONY: help install install-dev test lint format clean build run docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (flake8, mypy)"
	@echo "  format       - Format code (black, isort)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build executable"
	@echo "  build-debug  - Build executable with debug console"
	@echo "  run          - Run the application"
	@echo "  run-cli      - Run in command-line mode"
	@echo "  docs         - Generate documentation"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=keyreplacer --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 keyreplacer
	mypy keyreplacer --ignore-missing-imports

# Format code
format:
	black keyreplacer tests scripts
	isort keyreplacer tests scripts

# Check formatting without making changes
format-check:
	black --check keyreplacer tests scripts
	isort --check-only keyreplacer tests scripts

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.spec" -delete

# Build executable
build: clean
	python scripts/build.py --clean --install-deps

# Build executable with debug console
build-debug: clean
	python scripts/build.py --clean --install-deps --debug

# Run the application
run:
	python -m keyreplacer

# Run in command-line mode
run-cli:
	python -m keyreplacer --no-gui

# Generate documentation
docs:
	@echo "Documentation generation not implemented yet"

# Development workflow - format, lint, test
dev-check: format lint test
	@echo "Development checks passed!"

# Release workflow
release-check: format-check lint test
	@echo "Release checks passed!"

# Setup development environment
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make help' to see available commands."
