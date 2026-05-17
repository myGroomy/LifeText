.PHONY: help install dev test lint security docker-build docker-run clean setup-db

help:
	@echo "LifeText Development Tasks"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies"
	@echo "  make setup-db       Initialize database"
	@echo ""
	@echo "Development:"
	@echo "  make dev            Run development server"
	@echo "  make test           Run tests"
	@echo ""
	@echo "Quality:"
	@echo "  make lint           Run linting checks"
	@echo "  make security       Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Clean up artifacts"

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

dev:
	@echo "🚀 Starting development server..."
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	@echo "🔍 Running linting checks..."
	bash ci/lint.sh

security:
	@echo "🔐 Running security checks..."
	bash ci/security.sh

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t lifetext-api:latest .

docker-run:
	@echo "🐳 Running Docker Compose..."
	docker-compose up

setup-db:
	@echo "📦 Setting up database..."
	docker-compose exec api python scripts/init_db.py
	@echo "✅ Database initialized"

clean:
	@echo "🧹 Cleaning up artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned up"
