.PHONY: help install run test migrate migrate-create migrate-upgrade migrate-rollback migrate-history migrate-current migrate-pending clean

help: ## Show this help message
	@echo "DocHub Development Commands"
	@echo "=========================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pipenv install

run: ## Run the development server
	pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pipenv run pytest

# Migration commands
migrate: ## Show migration help
	@echo "Migration Commands:"
	@echo "  make migrate-create MSG='description'  - Create new migration"
	@echo "  make migrate-upgrade                   - Run all pending migrations"
	@echo "  make migrate-rollback REV=001         - Rollback to revision"
	@echo "  make migrate-history                   - Show migration history"
	@echo "  make migrate-current                   - Show current revision"
	@echo "  make migrate-pending                   - Show pending migrations"

migrate-create: ## Create a new migration (MSG='description')
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migrate-create MSG='description'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MSG)"

migrate-upgrade: ## Run all pending migrations
	alembic upgrade head

migrate-rollback: ## Rollback to a specific revision (REV=001)
	@if [ -z "$(REV)" ]; then \
		echo "Error: REV is required. Usage: make migrate-rollback REV=001"; \
		exit 1; \
	fi
	alembic downgrade "$(REV)"

migrate-history: ## Show migration history
	alembic history

migrate-current: ## Show current revision
	alembic current

migrate-pending: ## Show pending migrations
	alembic heads

# Docker commands
docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start all services
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## Show logs
	docker-compose logs -f

# Development commands
format: ## Format code with black and isort
	pipenv run black .
	pipenv run isort .

lint: ## Run linting
	pipenv run flake8 .

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Admin user commands
admin-create: ## Create admin user
	pipenv run python scripts/create_admin.py

init-data: ## Create initial data (admin user + department)
	pipenv run python scripts/init_data.py

test-admin: ## Test admin user functionality
	pipenv run python scripts/test_admin.py 

# Migration commands
migrate-dev-create:
	@echo "Creating migration for development environment..."
	@python scripts/migrate_dev.py create $(message)

migrate-dev-upgrade:
	@echo "Upgrading development database..."
	@python scripts/migrate_dev.py upgrade

migrate-dev-current:
	@echo "Current development database revision:"
	@python scripts/migrate_dev.py current

migrate-dev-history:
	@echo "Development migration history:"
	@python scripts/migrate_dev.py history

migrate-staging-upgrade:
	@echo "Upgrading staging database..."
	@python scripts/migrate_staging.py upgrade

migrate-staging-current:
	@echo "Current staging database revision:"
	@python scripts/migrate_staging.py current

migrate-prod-upgrade:
	@echo "Upgrading production database..."
	@python scripts/migrate_prod.py upgrade

migrate-prod-current:
	@echo "Current production database revision:"
	@python scripts/migrate_prod.py current

# Helper commands
migrate-help:
	@echo "Migration Commands:"
	@echo "  make migrate-dev-create message='Add user table'  - Create new migration"
	@echo "  make migrate-dev-upgrade                         - Upgrade dev database"
	@echo "  make migrate-dev-current                         - Show dev current revision"
	@echo "  make migrate-dev-history                         - Show dev migration history"
	@echo "  make migrate-staging-upgrade                     - Upgrade staging database"
	@echo "  make migrate-staging-current                     - Show staging current revision"
	@echo "  make migrate-prod-upgrade                        - Upgrade production database"
	@echo "  make migrate-prod-current                        - Show production current revision" 