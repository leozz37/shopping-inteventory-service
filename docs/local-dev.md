# Local Development Guide

## Prerequisites

Before starting local development, ensure you have the following installed:

### Required Tools

- **Python 3.13** (or compatible version)
  ```bash
  python --version
  # Should output: Python 3.13.x
  ```

- **Docker & Docker Compose**
  ```bash
  docker --version
  docker-compose --version
  ```

- **uv package manager**
  ```bash
  uv --version
  # Or install: curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **Make**
  ```bash
  make --version
  ```

- **jq** (optional, for parsing JSON in terminal)
  ```bash
  brew install jq  # macOS
  # or apt-get install jq  # Linux
  ```

### Recommended Tools

- **curl** – Test HTTP endpoints
- **git** – Version control
- **VS Code** – Code editor with Python and Pylance extensions

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jamble/shopping-inventory-service.git
cd shopping-inventory-service
```

### 2. Install Python Dependencies

The project uses `uv` for fast Python dependency management:

```bash
# Install all development dependencies
uv pip install -r services/api/requirements.txt
uv pip install -r services/orders_listener/requirements.txt
uv pip install -r integration_tests/requirements.txt

# Or use make target
make install
```

## Running Locally

### All Services

Start the entire application locally with Docker Compose:

```bash
make docker-up
```

This starts:
- **Firestore Emulator** (port 8080) – Local database
- **API Service** (port 8000) – FastAPI server
- **Orders Listener** (port 8001) – HTTP endpoint
- **Bridge** – Polling service for order detection
- **Seed Service** – Initializes test data
- **MailHog** (ports 1025, 8025) – SMTP sink & web UI

**Wait ~10 seconds** for services to stabilize, then verify:

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### Running Individual Services

#### API 

Run without Docker:

```bash
cd services/api/src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Orders Listener

Run with functions-framework:

```bash
cd services/orders_listener/src
python -m functions_framework --target=handle_order --debug --port 8001
```

Expected output:
```
 * Running on http://0.0.0.0:8001
 * Press CTRL+C to quit
```

#### Firestore Emulator

Run standalone (requires Node.js 18+):

```bash
# Install firebase-tools globally
npm install -g firebase-tools

# Start emulator in empty directory
mkdir -p /tmp/firestore_emulator
cd /tmp/firestore_emulator
firebase emulators:start --only firestore --host 0.0.0.0 --port 8080
```

#### MailHog (SMTP Testing)

Run standalone:

```bash
# Install MailHog
# macOS: brew install mailhog
# Or download from https://github.com/mailhog/MailHog/releases

mailhog
```

Then access web UI at `http://localhost:8025`.

## Testing

### Unit Tests

Run all unit tests:

```bash
make test
```

Run specific test file:

```bash
# API tests
make test-api

# Orders Listener tests
make test-listener
```

### Integration Tests

Requires Docker Compose:

```bash
make test-integration
```

This runs the full end-to-end flow:
1. Registers a user
2. Places an order
3. Verifies email in MailHog
4. Checks order status

Run specific integration test:

```bash
pytest integration_tests/test_integration_flow.py::test_order_flow -v -s
```

### Inspect Firestore Data

Using the Firebase Emulator UI:

1. Open http://localhost:4400 (Firestore UI)
2. Browse collections: Users, Products, Orders
3. View document contents and edit data

Or query via Python:

```python
from google.cloud import firestore

# Point to emulator
import os
os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'

db = firestore.Client(project='test-project')
orders = db.collection('Orders').stream()

for doc in orders:
    print(f'{doc.id}: {doc.to_dict()}')
```

## Common Development Tasks

### Testing Email Delivery

1. Start MailHog: Included in `make docker-up`

2. Place an order via API:
   ```bash
   # Get token
   TOKEN=$(curl -s -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "pass123"}' \
     | jq -r '.access_token')
   
   # Place order
   curl -X POST http://localhost:8000/orders/place \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"buyer_email": "test@example.com", "product_id": "product-1"}'
   ```

3. Check MailHog web UI: http://localhost:8025

4. Or query via API:
   ```bash
   curl http://localhost:8025/api/v1/messages
   ```

### Creating Test Data

Edit [integration_tests/seed_firestore_emulator.py](../../integration_tests/seed_firestore_emulator.py):

```python
# Add to main() function
db.collection('Products').document('product-2').set({
    'name': 'Widget B',
    'description': 'Another widget',
    'price': 29.99,
    'status': 'in_stock'
})
```

Then restart Docker Compose:

```bash
make docker-down
make docker-up
```
