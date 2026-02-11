# API Documentation

## Overview

The Shopping Inventory API is a FastAPI-based REST service that handles user registration, authentication, and order management. All endpoints are fully documented in OpenAPI 3.0 format and accessible via interactive Swagger UI.

## Base URL

- **Local Development:** `http://localhost:8000`
- **Production (GCP):** Deployed to Cloud Run URL provided by Terraform (Gozlan, check your email!)

## Authentication

The API uses **JWT (JSON Web Token)** authentication for protected endpoints.

### Getting a Token

1. Register a new user:
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepass123"}'
   ```

   Response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```

2. Or login with existing credentials:
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepass123"}'
   ```

### Using the Token

Include the token in the `Authorization` header for protected endpoints:

```bash
curl -X POST http://localhost:8000/orders/place \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"buyer_email": "user@example.com", "product_id": "product-1"}'
```

## Endpoints

### Health Check

**Endpoint:** `GET /health`

**Authentication:** None

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### User Registration

**Endpoint:** `POST /auth/register`

**Authentication:** None

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `400 Bad Request` – Invalid email or password format
- `409 Conflict` – Email already registered

**Example:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "password": "pass123"}'
```

---

### User Login

**Endpoint:** `POST /auth/login`

**Authentication:** None

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` – Invalid email or password
- `400 Bad Request` – Missing fields

**Example:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass123"}'
```

---

### Place Order

**Endpoint:** `POST /orders/place`

**Authentication:** Required (JWT Bearer token)

**Request Body:**
```json
{
  "buyer_email": "user@example.com",
  "product_id": "product-1"
}
```

**Response (201 Created):**
```json
{
  "order_id": "order-abc123xyz",
  "status": "pending",
  "buyer_email": "user@example.com",
  "product_id": "product-1",
  "created_at": "2026-02-11T12:34:56Z"
}
```

**Errors:**
- `401 Unauthorized` – Missing or invalid token
- `400 Bad Request` – Invalid request body
- `404 Not Found` – Product does not exist
- `500 Internal Server Error` – Database error

**Example:**
```bash
TOKEN="<your_jwt_token>"
curl -X POST http://localhost:8000/orders/place \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"buyer_email": "user@example.com", "product_id": "product-1"}'
```

---

## Interactive Documentation

Once the API is running, visit the interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`

Swagger provides full endpoint documentation, parameter descriptions, and the ability to test endpoints directly.

## Status Codes

| Code | Meaning |
|------|---------|
| `200` | OK – Request succeeded |
| `201` | Created – Resource created successfully |
| `400` | Bad Request – Invalid request body or parameters |
| `401` | Unauthorized – Missing or invalid token |
| `404` | Not Found – Resource does not exist |
| `409` | Conflict – Resource already exists (e.g., duplicate email) |
| `500` | Internal Server Error – Server-side error |

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error description here"
}
```

**Example:**
```json
{
  "detail": "User with email user@example.com already exists"
}
```

## Rate Limiting

Currently, no rate limiting is enforced. This may be added in future versions.

## Database Schema

### Users Collection

```json
{
  "email": "user@example.com",
  "password_hash": "$2b$12$...(bcrypt hash)..."
}
```

### Products Collection

```json
{
  "product_id": "product-1",
  "name": "Widget A",
  "status": "in_stock"
}
```

### Orders Collection

```json
{
  "buyer_email": "user@example.com",
  "product_id": "product-1",
  "status": "pending",
  "created_at": "2026-02-11T12:34:56Z"
}
```
