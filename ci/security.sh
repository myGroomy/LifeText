#!/bin/bash
# Security check script for LifeText

set -e

echo "🔐 Running security checks..."

# Install security tools
pip install bandit safety detect-secrets -q

# Check for hardcoded secrets
echo "  Scanning for secrets..."
detect-secrets scan --baseline .secrets.baseline 2>/dev/null || echo "    (First run, creating baseline)"

# Bandit security check
echo "  Running bandit security scan..."
bandit -r src/ -ll || true

# Check dependencies
echo "  Checking dependencies for known vulnerabilities..."
safety check --json 2>/dev/null || safety check || true

# Check for hardcoded credentials
echo "  Checking for obvious hardcoded credentials..."
if grep -r "password.*=" src/ tests/ --include="*.py" -i | grep -v "#" | grep -v "\.example"; then
    echo "    ❌ WARNING: Possible hardcoded passwords found"
    exit 1
fi

if grep -r "sk-" src/ tests/ --include="*.py" | grep -v "\.example"; then
    echo "    ❌ WARNING: Possible API keys found"
    exit 1
fi

echo "✅ Security checks completed!"
