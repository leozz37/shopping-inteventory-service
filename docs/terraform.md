# Terraform & Infrastructure Documentation

## Overview

This project uses **Terraform** to define and deploy infrastructure on **Google Cloud Platform (GCP)**. All infrastructure is treated as code, version-controlled, and reproducible across environments.

### Infrastructure Managed by Terraform

- **Cloud Run Services** – FastAPI application (API)
- **Cloud Functions** – Orders Listener (HTTP-triggered)
- **Firestore Database** – Document store for users, products, orders
- **Cloud Storage** – Function source code, Terraform state
- **Artifact Registry** – Docker image repository
- **IAM Roles & Service Accounts** – Security and permissions
- **Cloud Secrets** – Sensitive environment variables

## Project Structure

```
terraform/
├── main.tf                      # Provider configuration
├── providers.tf                 # GCP provider setup
├── versions.tf                  # Required versions
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
│
├── services.tf                  # Enable GCP APIs/services
├── iam_artifact_registry.tf     # Artifact Registry IAM
├── artifact_registry.tf         # Container registry
├── cloud_run.tf                 # Cloud Run API service
├── cloud_functions.tf           # Orders Listener function
├── firestore.tf                 # Firestore database
├── secretmanager.tf             # Secrets management
├── github_actions_sa.tf         # GitHub Actions service account
│
├── envs/
│   ├── dev/
│   │   └── terraform.tfvars     # Development environment
│   └── ci/
│       └── terraform.tfvars     # CI environment
│
├── terraform.tfstate            # Current state (local, git-ignored)
└── terraform.tfstate.backup     # State backup
```

## Prerequisites

Before deploying, ensure you have:

### Tools

1. **Terraform** 1.0+
   ```bash
   terraform --version
   ```

2. **gcloud CLI**
   ```bash
   gcloud --version
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Google Cloud Project**
   - GCP project created and billing enabled
   - Project ID accessible:
     ```bash
     gcloud config get-value project
     ```

### GCP Permissions

Your GCP user account requires:
- `Editor` or custom role with permissions for:
  - Cloud Run
  - Cloud Functions
  - Firestore
  - Cloud Storage
  - Artifact Registry
  - Service Accounts
  - IAM

### Build Artifacts

Before applying Terraform:

1. **Orders Listener Function ZIP**
   ```bash
   make orders-fn-zip
   # Creates: dist/orders_listener.zip
   ```

## Configuration

### Environment Variables

Store environment config in `envs/ENV/terraform.tfvars`:

```hcl
# envs/dev/terraform.tfvars
project_id           = "your-gcp-project-id"
region                = "us-central1"
environment           = "dev"
api_image_uri         = "us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:latest"
orders_listener_zip   = "../dist/orders_listener.zip"
```

### Environment-Specific Settings

#### Development (`envs/dev/`)

```hcl
project_id        = "jamble-dev"
region            = "us-central1"
environment       = "dev"
firestore_region  = "us-central1"
api_replicas      = 1
api_memory        = "512Mi"
function_memory   = 256
```

#### CI/Testing (`envs/ci/`)

```hcl
project_id        = "jamble-ci"
region            = "us-central1"
environment       = "ci"
firestore_region  = "us-central1"
api_replicas      = 1
api_memory        = "256Mi"
function_memory   = 128
```

## Variables Reference

### Input Variables

**[terraform/variables.tf](../../terraform/variables.tf)**

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `project_id` | string | Yes | GCP project ID |
| `region` | string | No | Default: `us-central1` |
| `environment` | string | No | Deployment environment (dev/ci/prod) |
| `api_image_uri` | string | Yes | Docker image for API |
| `orders_listener_zip` | string | Yes | Path to orders_listener.zip |
| `firestore_region` | string | No | Firestore location; Default: `us-central1` |
| `api_replicas` | number | No | Cloud Run replicas; Default: 1 |
| `api_memory` | string | No | Cloud Run memory; Default: `512Mi` |
| `function_memory` | number | No | Cloud Function memory MB; Default: 256 |

### Output Values

**[terraform/outputs.tf](../../terraform/outputs.tf)**

| Output | Description |
|--------|-------------|
| `api_service_url` | Cloud Run API endpoint |
| `orders_listener_url` | Cloud Function HTTPS endpoint |
| `firestore_database` | Firestore database ID |
| `artifact_registry_url` | Docker registry URL |

Retrieve outputs after apply:
```bash
terraform output api_service_url
terraform output orders_listener_url
```

## Deployment

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

This:
- Downloads provider plugins
- Initializes state backend (GCS)
- Sets up working directory

### 2. Build Function ZIP

```bash
make orders-fn-zip
# Creates: dist/orders_listener.zip
```

### 3. Plan Changes

```bash
# Use development environment
terraform plan -var-file=envs/dev/terraform.tfvars

# Or set project interactively
terraform plan
```

Review the plan output. It shows:
- Resources to create/modify/destroy
- Properties being changed
- Dependencies

### 4. Apply Configuration

```bash
terraform apply -var-file=envs/dev/terraform.tfvars
```

You'll be prompted to confirm. Type `yes` to proceed.

Expected output:
```
Apply complete! Resources created: 15
api_service_url = "https://api-xxxxx-uc.a.run.app"
orders_listener_url = "https://us-central1-project.cloudfunctions.net/orders-listener"
```

### 5. Verify Deployment

```bash
# Get API URL
API_URL=$(terraform output -raw api_service_url)

# Test health endpoint
curl "$API_URL/health"
# Expected: {"status":"ok"}

# Test API
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

## State Management

### State File

Terraform state is stored in **Google Cloud Storage** (configured in `main.tf`):

```hcl
terraform {
  backend "gcs" {
    bucket = "jamble-terraform-state"
    prefix = "terraform/state"
  }
}
```

### State in Git

⚠️ **Never commit `terraform.tfstate` to version control!**

State files contain secrets and are git-ignored. To share state across team members:

- Use GCS backend (already configured)
- Ensure team members have GCS access:
  ```bash
  gsutil iam ch user@example.com:roles/storage.admin \
    gs://jamble-terraform-state
  ```

### Backup & Recovery

Automatic backups stored in GCS:
```bash
# List state versions
gsutil ls gs://jamble-terraform-state/terraform/state/

# Download previous state if needed
gsutil cp gs://jamble-terraform-state/terraform/state/default.tfstate.backup .
```

## Common Operations

### Update API Docker Image

1. Build new image:
   ```bash
   docker build -t us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.2 \
     services/api/
   docker push us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.2
   ```

2. Update variable:
   ```bash
   # Edit envs/dev/terraform.tfvars or use -var flag
   terraform apply -var-file=envs/dev/terraform.tfvars \
     -var="api_image_uri=us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.2"
   ```

### Scale API Service

```bash
terraform apply -var-file=envs/dev/terraform.tfvars \
  -var="api_replicas=3" \
  -var="api_memory=1Gi"
```

### Increase Function Memory

```bash
terraform apply -var-file=envs/dev/terraform.tfvars \
  -var="function_memory=512"
```

### Destroy All Resources

⚠️ **Warning:** This permanently deletes all infrastructure.

```bash
terraform destroy -var-file=envs/dev/terraform.tfvars
```

Confirm by typing `yes`.

## Troubleshooting

### "Error: Resource already exists"

**Problem:** Terraform can't create a resource because it already exists.

**Solution:** Import the existing resource into state:
```bash
terraform import google_cloud_run_service.api \
  projects/PROJECT_ID/locations/REGION/services/api
terraform plan  # Should show no changes
```

### "Error: Authentication required"

**Problem:** Terraform can't authenticate with GCP.

**Solutions:**

1. Login with gcloud:
   ```bash
   gcloud auth application-default login
   gcloud auth login
   ```

2. Set project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Verify credentials:
   ```bash
   gcloud config list
   ```

### "Error: Permission denied"

**Problem:** User account lacks required permissions.

**Solutions:**

1. Grant Editor role (if owner of project):
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member=user:YOUR_EMAIL \
     --role=roles/editor
   ```

2. Or grant specific roles:
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member=user:YOUR_EMAIL \
     --role=roles/cloudfunctions.developer
   ```

### State lock timeout

**Problem:** Another operation is modifying state.

**Solutions:**

1. Wait for other operation to complete.

2. Force unlock (dangerous, only if sure operation failed):
   ```bash
   terraform force-unlock LOCK_ID
   ```

### GCS bucket already exists

**Problem:** State backend storage already exists.

**Solution:** Use existing bucket name in `main.tf`:
```hcl
backend "gcs" {
  bucket = "existing-jamble-terraform-state"
}
```

## Resource Details

### Cloud Run (API)

**Terraform:** [terraform/cloud_run.tf](../../terraform/cloud_run.tf)

Configuration:
- **Runtime:** Python (via Docker image)
- **Memory:** 512MB (configurable)
- **CPU:** 2 vCPU (auto-allocated)
- **Concurrency:** 80 (max concurrent requests per instance)
- **Timeout:** 300 seconds
- **Environment variables:** Firestore emulator disabled (use real Firestore)

Endpoint: `https://api-xxxxx-uc.a.run.app`

### Cloud Functions (Orders Listener)

**Terraform:** [terraform/cloud_functions.tf](../../terraform/cloud_functions.tf)

Configuration:
- **Runtime:** Python 3.13
- **Memory:** 256MB (configurable)
- **Timeout:** 30 seconds
- **Trigger:** HTTPS endpoint
- **Source:** GCS (orders_listener.zip)

Endpoint: `https://us-central1-PROJECT_ID.cloudfunctions.net/orders-listener`

### Firestore Database

**Terraform:** [terraform/firestore.tf](../../terraform/firestore.tf)

Configuration:
- **Location:** us-central1 (configurable)
- **Mode:** Datastore (Native)
- **Collections:** Users, Products, Orders
- **Automatic backups:** Enabled (30+ day retention)

### Service Accounts & IAM

**Terraform:** [terraform/github_actions_sa.tf](../../terraform/github_actions_sa.tf)

Service accounts created:
- `github-actions-sa` – CI/CD deployments
  - Permissions: Cloud Run deployer, Function deployer, Storage admin
  - Workload identity federated with GitHub

### Cloud Storage (Artifact Registry State)

**Terraform:** [terraform/artifact_registry.tf](../../terraform/artifact_registry.tf)

Repositories:
- `jamble-registry` – Docker image repository for API/function images
- Private, accessible only to project members

## GitHub Actions Integration

### Automated Deployments

The `deploy.yml` workflow runs Terraform on merge to main:

1. Initializes Terraform
2. Plans changes (commented on PR)
3. Applies on merge (requires approval in workflow)

### Workload Identity Federation

GitHub Actions authenticates without long-lived service account keys:

```yaml
# .github/workflows/deploy.yml
- uses: google-github-actions/auth@v1
  with:
    workload-identity-provider: projects/PROJECT_ID/locations/global/workloadIdentityPools/github/providers/github
    service-account: github-actions@PROJECT_ID.iam.gserviceaccount.com
```

## Best Practices

1. **Always plan before apply**
   ```bash
   terraform plan -var-file=envs/dev/terraform.tfvars
   ```

2. **Use tfvars files, not command-line flags**
   - Better for reproducibility
   - Easier to track in version control

3. **Separate state per environment**
   - Never mix dev and prod in same state file

4. **Backup state regularly**
   ```bash
   gsutil cp gs://jamble-terraform-state terraform/
   ```

5. **Review change history**
   ```bash
   terraform show  # Current state
   ```

6. **Test changes in dev first**
   ```bash
   terraform apply -var-file=envs/dev/terraform.tfvars
   ```

## Next Steps

- Review [Architecture Documentation](architecture.md) for system design
- Check [Local Development Guide](local-dev.md) for local setup
- Read [Runbooks](runbooks.md) for operational procedures
- Explore GCP Console for deployed resources:
  ```bash
  gcloud console
  ```
