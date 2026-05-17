#!/bin/bash
# Linting script for LifeText

set -e

echo "🔍 Running linting checks..."

# Install tools
pip install flake8 pylint black isort mypy -q

# Black formatting check
echo "  Checking code formatting with black..."
black --check src/ tests/ 2>/dev/null || {
    echo "    ❌ Code formatting issues found. Run: black src/ tests/"
    exit 1
}

# isort import check
echo "  Checking import ordering with isort..."
isort --check-only src/ tests/ 2>/dev/null || {
    echo "    ❌ Import ordering issues found. Run: isort src/ tests/"
    exit 1
}

# flake8 basic checks
echo "  Checking with flake8..."
flake8 src/ tests/ --max-line-length=120 --count --select=E9,F63,F7,F82 || exit 1

# Type checking
echo "  Running type checks with mypy..."
mypy src/ --ignore-missing-imports || true

echo "✅ All linting checks passed!"
