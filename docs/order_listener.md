# Orders Listener Documentation

## Overview

The Orders Listener is a Google Cloud Function that monitors the Firestore `Orders` collection in real time and triggers business logic when new orders are placed. In the local development environment, it runs as a Python server via `functions-framework`, with a polling bridge that detects new orders and triggers the function.

## Architecture

### Components

```
API (FastAPI)
    ↓
    [Place Order]
    ↓
Firestore: Orders Collection
    ↓
    [New Order Document]
    ↓
Bridge (Polling Loop, every 2 seconds)
    ↓
    [POST /orders endpoint]
    ↓
Orders Listener Function
    ↓
    [Email Notification]
    ↓
MailHog (Local) / SendGrid (Production)
```

### Async Pattern

The Orders Listener operates asynchronously:
1. User places an order via the API → Firestore Orders collection updated
2. Bridge polls Orders collection (configurable interval, default 2s)
3. New orders detected → Bridge POSTs to Orders Listener endpoint
4. Orders Listener processes order and sends email notification
5. User receives confirmation email

This decoupling ensures order placement completes quickly without waiting for email delivery.

## Local Development Setup

### Docker Compose Services

The `integration_tests/docker-compose.yml` orchestrates the Orders Listener locally:

- **orders_listener:** HTTP server running `functions-framework` on port 8001
- **orders_listener_bridge:** Polling process that detects new orders
- **firestore:** Emulator providing Firestore instance on port 8080
- **mailhog:** SMTP sink for testing email delivery on port 1025

## Orders Listener Function

### Location

[services/orders_listener/src/main.py](../../services/orders_listener/src/main.py)

### Entry Point

```python
def handle_order(request):
```

### Responsibilities

1. **Receive Order Event**
   - HTTP endpoint: `POST /orders`
   - Expected request body contains `order_id`, `buyer_email`, `product_id`

2. **Validate Order**
   - Check that order exists in Firestore
   - Verify product_id is valid

3. **Send Confirmation Email**
   - Compose order confirmation message
   - Send via email service (MailHog locally, SendGrid in production)
   - Include order details, product info, and buyer email

4. **Log Activity**
   - Log successful email sends
   - Log errors for debugging

### Configuration

**Environment Variables:**

| Variable | Purpose | Local Value | Production |
|----------|---------|-------------|-----------|
| `FIRESTORE_EMULATOR_HOST` | Firestore emulator address | `localhost:8080` | Not set (use real Firestore) |
| `SMTP_HOST` | Email service hostname | `mailhog` | SendGrid API |
| `SMTP_PORT` | Email service port | `1025` | 587 |
| `SMTP_USER` | Email service username | `test` | SendGrid API key |
| `SMTP_PASSWORD` | Email service password | `test` | SendGrid API key |
| `FROM_EMAIL` | Sender email address | `noreply@jamble.local` | `noreply@jamble-app.com` |

## Bridge Pattern

The bridge connects the Firestore Orders collection (local emulator or real Firestore) to the Orders Listener HTTP endpoint. It polls for new orders and triggers the function.

## Testing

### Unit Tests

**Location:** [services/orders_listener/tests/](../../services/orders_listener/tests/)

Run locally:
```bash
make test
```

Test files:
- `test_main.py` – Handler endpoint tests
- `test_email_client.py` – Email sending logic
- `test_firestore_client.py` – Firestore queries

### Integration Tests

**Location:** [integration_tests/test_integration_flow.py](../../integration_tests/test_integration_flow.py)

Run with Docker Compose:
```bash
make test-integration
```

This test:
1. Registers a user
2. Places an order via API
3. Waits for Orders Listener to process
4. Checks MailHog for confirmation email

## Production Deployment

### Cloud Function Configuration

Terraform deploys the Orders Listener to **Google Cloud Functions**:

**Terraform Resource:** [terraform/cloud_functions.tf](../../terraform/cloud_functions.tf)

### Production Environment Variables

In production:
- `FIRESTORE_EMULATOR_HOST` is **not set** (uses real Firestore)
- `SMTP_HOST` points to SendGrid or equivalent email service
- `GOOGLE_APPLICATION_CREDENTIALS` references Cloud Function's built-in service account

### Deployment Process

1. Create orders_listener.zip:
   ```bash
   make orders-fn-zip
   ```

2. Deploy with Terraform:
   ```bash
   cd terraform
   terraform apply
   ```

The Terraform configuration:
- Uploads ZIP to Google Cloud Storage
- Creates Cloud Function from ZIP
- Sets environment variables
- Configures IAM permissions
- Returns HTTPS endpoint URL

### Email Verification (Local)

MailHog web interface:
```
http://localhost:8025
```

Shows:
- All emails sent (even if SMTP fails)
- Email content, headers, and recipients
- Useful for testing email templates
