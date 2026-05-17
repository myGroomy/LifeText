#!/bin/bash
# Test script for LifeText

set -e

echo "🧪 Running tests..."

# Install test dependencies
pip install pytest pytest-cov -q

# Run tests with coverage
echo "  Running pytest with coverage..."
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests completed!"
echo "   Coverage report: htmlcov/index.html"
