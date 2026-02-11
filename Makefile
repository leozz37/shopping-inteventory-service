PROJECT_NAME := inventory-platform
API_DIR := services/api/src
API_ROOT_DIR := services/api
FUNCTION_DIR := services/functions/orders_listener
TERRAFORM_DIR := terraform
PYTHON := uv run python
ORDERS_ROOT_DIR := services/orders_listener
ORDERS_FN_DIR := services/orders_listener/src
ORDERS_FN_ZIP := dist/orders_listener.zip

# Local DEV
install: # Install dependencies (uv)
	cd $(API_DIR) && uv sync

run: # Run FastAPI locally with reload
	cd $(API_DIR) && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

.PHONY: test
test: # Run all unit tests
	COVERAGE_FILE=$(CURDIR)/.coverage \
		cd $(API_ROOT_DIR) && uv run pytest tests/ -v --cov=src --cov-append
	COVERAGE_FILE=$(CURDIR)/.coverage \
		cd $(ORDERS_ROOT_DIR) && PYTHONPATH=src uv run pytest tests/ -v --cov=src --cov-append

test-api: # Run unit tests for API (coverage appended to repo .coverage)
	COVERAGE_FILE=$(CURDIR)/.coverage \
		cd $(API_ROOT_DIR) && uv run pytest tests/ -v --cov=src --cov-append --cov-report=term-missing

test-listener: # Run unit tests for orders listener (coverage appended to repo .coverage)
	COVERAGE_FILE=$(CURDIR)/.coverage \
		cd $(ORDERS_ROOT_DIR) && PYTHONPATH=src uv run pytest tests/ -v --cov=src --cov-append --cov-report=term-missing

.PHONY: coverage-report
coverage-report: # Generate coverage reports from combined .coverage
	uv run coverage report -m
	uv run coverage html

lint: # Run linter (ruff)
	cd $(API_DIR) && uv run ruff check .

format: # Auto-format code
	cd services && uv run ruff format .

export-reqs: # Export requirements.txt from lock file
	cd $(API_ROOT_DIR) && uv export --format requirements-txt --output-file requirements.txt

# Local Docker
DOCKER_IMAGE := inventory-api
DOCKERFILE := ./services/api/Dockerfile
DOCKER_CONTEXT := .
COMPOSE_FILE := integration_tests/docker-compose.yml

docker-build: # Build API Docker image
	docker build \
		-t $(DOCKER_IMAGE) \
		-f $(DOCKERFILE) \
		$(DOCKER_CONTEXT)

docker-run: # Run API container locally
	docker run --rm \
		-p 8000:8080 \
		--env-file .env \
		$(DOCKER_IMAGE)

docker-up: # Run API using docker compose
	docker compose -f $(COMPOSE_FILE) up --build

docker-down: # Stop docker compose
	docker compose -f $(COMPOSE_FILE) down

.PHONY: test-integration

test-integration: # Run docker compose (if needed) and integration tests
	@if [ -z "$$(docker compose -f $(COMPOSE_FILE) ps -q)" ]; then \
		echo "Starting docker compose..."; \
		docker compose -f $(COMPOSE_FILE) up -d --build; \
	fi
	@echo "Waiting for orders_listener..."
	@i=0; \
	until curl -s http://localhost:8081/ >/dev/null 2>&1; do \
		i=$$((i+1)); \
		if [ $$i -ge 30 ]; then echo "orders_listener not ready"; exit 1; fi; \
		sleep 1; \
	done
	@echo "Waiting for MailHog..."
	@i=0; \
	until curl -s http://localhost:8025/ >/dev/null 2>&1; do \
		i=$$((i+1)); \
		if [ $$i -ge 30 ]; then echo "MailHog not ready"; exit 1; fi; \
		sleep 1; \
	done
	pytest integration_tests -v
	docker compose -f $(COMPOSE_FILE) down

.PHONY: orders-fn-zip
orders-fn-zip:
	@echo "📦 Building orders_listener Cloud Function zip"
	@mkdir -p dist
	@cd $(ORDERS_FN_DIR) && zip -r $(CURDIR)/$(ORDERS_FN_ZIP) . > /dev/null
	@echo "✅ Created $(ORDERS_FN_ZIP)"

# Terraform
TF_DIR := terraform
TF_VARS_DEV := envs/dev/terraform.tfvars

.PHONY: tf-plan
tf-plan:
	cd $(TF_DIR) && terraform plan -var-file=$(TF_VARS_DEV)

.PHONY: tf-apply-auto
tf-apply:
	cd $(TF_DIR) && terraform apply -auto-approve -var-file=$(TF_VARS_DEV)
