PROJECT_NAME := inventory-platform
API_DIR := services/api
FUNCTION_DIR := services/functions/orders_listener
TERRAFORM_DIR := infra/terraform
PYTHON := uv run python

# Local DEV
install: # Install dependencies (uv)
	cd $(API_DIR) && uv sync

run: # Run FastAPI locally with reload
	cd $(API_DIR) && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

test: # Run unit tests
	cd $(API_DIR) && uv run pytest -q

lint: # Run linter (ruff)
	cd $(API_DIR) && uv run ruff check .

format: # Auto-format code
	cd $(API_DIR) && uv run ruff format .

export-reqs: # Export requirements.txt from lock file
	cd $(API_DIR) && uv export --format requirements-txt --output requirements.txt
