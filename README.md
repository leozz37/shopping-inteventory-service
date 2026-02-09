# 📦 Shopping Inventory Service

[![Pytest API](https://github.com/leozz37/shopping-inteventory-service/actions/workflows/python.yml/badge.svg)](https://github.com/leozz37/shopping-inteventory-service/actions/workflows/python.yml)
[![Docker Image](https://github.com/leozz37/shopping-inteventory-service/actions/workflows/docker-image.yml/badge.svg)](https://github.com/leozz37/shopping-inteventory-service/actions/workflows/docker-image.yml)
[![Terraform](https://github.com/leozz37/shopping-inteventory-service/actions/workflows/terraform.yml/badge.svg)](https://github.com/leozz37/shopping-inteventory-service/actions/workflows/terraform.yml)

A simple Inventory API that covers user registration, authentication (JWT), health checks, and order placement! API documented with OpenAPI (Swagger) and ready to run locally, with Docker Compose with local GCP infra, and provisioned via Terraform.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Running Locally](#running-locally)
  - [Running with Docker](#running-with-docker)
  - [Running with Docker Compose](#running-with-docker-compose)
- [Infrastructure with Terraform](#infrastructure-with-terraform)
  - [Terraform Prerequisites](#terraform-prerequisites)
  - [Initializing Terraform](#initializing-terraform)
  - [Planning Changes](#planning-changes)
  - [Applying Infrastructure](#applying-infrastructure)
  - [Destroying Infrastructure](#destroying-infrastructure)
- [Running Tests](#running-tests)
- [Running Linters](#running-linters)
- [Environment Variables](#environment-variables)

## ✅ Requirements

Before getting started, make sure you have the following installed:

- **Python 3.13**  
  Used to run the application locally and for development: [Download](https://www.python.org/downloads/release/python-3130/)

- **uv**  
  A fast Python package manager and virtual environment tool.  
  Used to install dependencies and manage the local environment.

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **Docker**  
  Required to build and run the application in containers: [Download](https://docs.docker.com/engine/install/)

- **Terraform (≥ 1.x)**  
  Used to provision and manage infrastructure as code: [Download](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)


You can verify installations with:

```bash
python --version
uv --version
docker --version
terraform version
```

## Overview

This project exposes a REST API for:

- Health checking the service
- Registering new users
- Authenticating users and issuing JWTs
- Placing orders

The API is fully described using **OpenAPI 3.0**, and the infrastructure can be provisioned automatically using **Terraform**.

## Tech Stack

- Python (FastAPI)
- JWT authentication
- OpenAPI / Swagger
- Docker and Docker Compose
- Terraform (IaC)
- Local Firestore for testing

## Getting Started

### Running Locally

1. Create and activate a virtual environment:

```bash
make install
```

2. Run the application (uv automatically creates a virtual env):

```bash
make run
```

The API will be available at:

```text
http://localhost:8000
```

### Running with Docker

1. Regenate the `requirements.txt` file from the `pyproject.toml`:

```bash
make export-reqs
```

2. Build the image:

```bash
make docker-build
```

3. Run the container:

```bash
make docker-run
```

### Running with Docker Compose

This is ideally for testing all the components of the API and running the full stack locally. It will run a container for the API, a local Firebase and will populate the firebase with a Product item.

1. Run everything:

```bash
docker-compose up --build
```

2. To stop everything:

```bash
docker-compose down
```

## Infrastructure with Terraform

Terraform is used to provision the infrastructure required to run the Inventory API on Google Cloud Platform (for example: cloud resources, networking, container services, etc.).

> Terraform files live in the infra/terraform/ directory.

Terraform Prerequisites:

- Terraform ≥ 1.x
- GCP credentials configured

Check version:

```bash
terraform version
```

Initializing Terraform:

```bash
cd infra/terraform
terraform init
```

Planning Changes:

```bash
terraform plan
```

Applying Infrastructure:

```bash
terraform apply
```

Destroying Infrastructure:

```bash
terraform destroy
```

> Warning: This will permanently delete all managed resources.

## Running Tests

Run all tests:

```bash
make test
```

## Running Linters

Ruff is the default linter. To run it:

```bash
make lint
```

To format the code and adapt it to the linter:

```bash
make format
```

## Environment Variables

Check the [`.env.example`](./services/api/src/.env.example) to see the required and defaults env vars:

```env
JWT_SECRET=super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

Make sure these are set locally, in Docker, and (when applicable) via Terraform-managed secrets or environment variables.