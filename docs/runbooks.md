# Runbooks & Operations Guide

## Overview

This document provides operational playbooks for running, monitoring, troubleshooting, and maintaining the Shopping Inventory Service in both local development and production environments.

## Table of Contents

1. [Deployment](#deployment)
2. [Monitoring](#monitoring)
3. [Troubleshooting](#troubleshooting)
4. [Scaling](#scaling)
5. [Backup & Disaster Recovery](#backup--disaster-recovery)
6. [Known Issues](#known-issues)

---

## Deployment

### Initial Deployment to Production

**Prerequisites:**
- GCP project with billing enabled
- Service account with appropriate permissions
- `make orders-fn-zip` executed locally

**Steps:**

1. **Configure environment variables**
   ```bash
   cd terraform
   # Edit envs/prod/terraform.tfvars
   # Set: project_id, region, api_image_uri
   ```

2. **Build and push API Docker image**
   ```bash
   docker build -t us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:latest \
     services/api/
   docker push us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:latest
   ```

3. **Create function ZIP**
   ```bash
   make orders-fn-zip
   ```

4. **Plan infrastructure**
   ```bash
   cd terraform
   terraform plan -var-file=envs/prod/terraform.tfvars
   # Review all resources to be created
   ```

5. **Apply infrastructure**
   ```bash
   terraform apply -var-file=envs/prod/terraform.tfvars
   # Confirm by typing: yes
   ```

6. **Verify deployment**
   ```bash
   API_URL=$(terraform output -raw api_service_url)
   curl "$API_URL/health"
   # Expected: {"status":"ok"}
   ```

7. **Test end-to-end flow**
   ```bash
   # Register user
   curl -X POST "$API_URL/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}'
   
   # Extract token
   TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}' | jq -r '.access_token')
   
   # Place order
   curl -X POST "$API_URL/orders/place" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"buyer_email": "test@example.com", "product_id": "product-1"}'
   ```

### Rolling Update (Existing Deployment)

To update API or Orders Listener after initial deployment:

1. **Update image/function**
   ```bash
   # For API: Rebuild and push Docker image
   docker build -t us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.1 \
     services/api/
   docker push us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.1
   
   # For Orders Listener: Rebuild ZIP
   make orders-fn-zip
   ```

2. **Plan changes**
   ```bash
   cd terraform
   terraform plan -var-file=envs/prod/terraform.tfvars \
     -var="api_image_uri=us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.1"
   ```

3. **Apply update**
   ```bash
   terraform apply -var-file=envs/prod/terraform.tfvars \
     -var="api_image_uri=us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.1"
   ```

4. **Verify**
   ```bash
   # Wait ~2 minutes for Cloud Run to deploy new revision
   API_URL=$(terraform output -raw api_service_url)
   curl "$API_URL/health"
   ```

### Rollback to Previous Version

If a deployment has issues:

1. **Identify previous image**
   ```bash
   gcloud run describe api --region us-central1 --format="value(status.activeRevisions[0].imageUri)"
   ```

2. **Rollback via Cloud Run**
   ```bash
   gcloud run services update-traffic api --to-revisions PREVIOUS_REVISION_ID=100
   ```

   Or reapply Terraform with previous image version:
   ```bash
   cd terraform
   terraform apply -var-file=envs/prod/terraform.tfvars \
     -var="api_image_uri=us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:v1.0"
   ```

3. **Verify rollback**
   ```bash
   API_URL=$(terraform output -raw api_service_url)
   curl "$API_URL/health"
   ```

---

## Monitoring

### Health Checks

**API Endpoint:**
```bash
API_URL=$(gcloud run services describe api --region us-central1 --format="value(status.url)")
curl "$API_URL/health"
# {status: "ok"} = healthy
```

**Orders Listener:**
```bash
# Test via ordering flow (emits POST to Orders Listener)
# Check order status and email delivery
```

### Logs

#### API Logs

**Cloud Logging (Production):**
```bash
# View recent logs
gcloud functions logs read api --limit 50

# View with filtering
gcloud functions logs read api --limit=50 --filter="severity=ERROR"

# Stream logs live
gcloud functions logs read api --limit=0 --follow
```

**Local (Docker):**
```bash
docker-compose -f integration_tests/docker-compose.yml logs -f api
```

#### Orders Listener Logs

**Cloud Logging (Production):**
```bash
gcloud functions logs read orders-listener --limit 50
```

**Local (Docker):**
```bash
docker-compose -f integration_tests/docker-compose.yml logs -f orders_listener
```

### Metrics

**Cloud Monitoring Dashboard:**

1. Open [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to Monitoring → Dashboards
3. Create custom dashboard with:
   - Cloud Run request rate
   - Cloud Function execution time
   - Firestore read/write operations
   - Error rates

**CLI:**
```bash
# Check Cloud Run metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"' \
  --format="table(metric.labels.service_name, points[0].value.double_value)"
```

### Email Delivery Verification

**Production (SendGrid/Email Provider):**

Monitor via provider's dashboard or email logs in code.

**Local (MailHog):**

```bash
# Check all emails
curl http://localhost:8025/api/v1/messages

# Check specific email
curl http://localhost:8025/api/v1/messages/1 | jq .
```

---

## Troubleshooting

### API Service Unavailable

**Symptoms:** `curl` returns 503 or connection refused

**Diagnosis:**

1. Check service status:
   ```bash
   gcloud run services describe api --region us-central1 --format="value(status.conditions[*].status)"
   ```

2. View recent logs:
   ```bash
   gcloud functions logs read api --limit 50
   ```

3. Check for deployment errors:
   ```bash
   gcloud run revisions list --format="table(name,status)"
   ```

**Solutions:**

1. **If image pull failed:**
   ```bash
   # Rebuild and push image
   docker build -t us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:latest \
     services/api/
   docker push us-central1-docker.pkg.dev/PROJECT_ID/jamble-registry/api:latest
   
   # Re-apply Terraform
   cd terraform && terraform apply -var-file=envs/prod/terraform.tfvars
   ```

2. **If startup fails:**
   ```bash
   # Check logs for error details
   gcloud run revisions list --format="table(name,status)"
   
   # Rollback to previous version
   gcloud run services update-traffic api --to-revisions PREVIOUS_REVISION=100
   ```

3. **If database unreachable:**
   ```bash
   # Verify Firestore is operational
   gcloud firestore databases describe
   
   # Check firestore API enabled
   gcloud services list --enabled | grep firestore
   ```

### High Error Rate

**Symptoms:** Errors in logs, 5xx responses increasing

**Diagnosis:**

1. Check error logs:
   ```bash
   gcloud functions logs read api --limit=100 --filter='severity=ERROR'
   ```

2. Identify error pattern:
   ```bash
   # Authentication errors?
   gcloud functions logs read api --filter='error="401"' --limit=50
   
   # Database errors?
   gcloud functions logs read api --filter='error="Firestore"' --limit=50
   ```

**Solutions:**

1. **Authentication issues:**
   - Verify `JWT_SECRET` environment variable is set
   - Check token expiry settings
   - Review IAM permissions

2. **Database issues:**
   - Check Firestore quota and monitoring
   - Scale if hitting rate limits
   - Restart connection pool (redeploy with Terraform)

3. **Resource constraints:**
   - Increase memory:
     ```bash
     terraform apply -var-file=envs/prod/terraform.tfvars \
       -var="api_memory=1Gi"
     ```
   - Increase replicas:
     ```bash
     terraform apply -var-file=envs/prod/terraform.tfvars \
       -var="api_replicas=3"
     ```

### Orders Not Processing

**Symptoms:** Order placed but no confirmation email received

**Diagnosis:**

1. Verify order created:
   ```bash
   gcloud firestore documents list --collection-id=Orders
   ```

2. Check Orders Listener logs:
   ```bash
   gcloud functions logs read orders-listener --limit 50
   ```

3. Verify email service:
   - In production: Check SendGrid/email provider dashboard
   - Locally: Check MailHog at http://localhost:8025

**Solutions:**

1. **If order not created:**
   - Check API logs for errors
   - Verify Firestore is accessible from Cloud Run
   - Test with manual order insert via Firestore CLI

2. **If function not triggered:**
   - In local dev: Verify bridge is running
     ```bash
     docker-compose -f integration_tests/docker-compose.yml ps orders_listener_bridge
     ```
   - In production: Verify function exists and is accessible
     ```bash
     gcloud functions describe orders-listener --region us-central1
     ```

3. **If email not sent:**
   - Check SMTP credentials
   - Verify email address is valid
   - Check email provider logs (SendGrid, etc.)
   - Review function logs for SMTP errors:
     ```bash
     gcloud functions logs read orders-listener --filter='SMTP' --limit=50
     ```

### Database Quota Exceeded

**Symptoms:** `RESOURCE_EXHAUSTED` errors, `429` responses

**Diagnosis:**

1. Check Firestore usage:
   ```bash
   gcloud firestore databases describe
   # Review: reads, writes, deletes
   ```

2. Check project quotas:
   ```bash
   gcloud compute project-info describe --format="value(quotas)"
   ```

**Solutions:**

1. **Request quota increase:**
   ```bash
   # Open Google Cloud Console → APIs & Services → Quotas
   # Search for "Firestore" quotas and request increase
   ```

2. **Optimize queries:**
   - Add indexes for complex queries
   - Batch operations
   - Cache frequently accessed data

3. **Scale database:**
   ```bash
   # Firestore scales automatically, but may need time
   # Monitor usage and adjust as needed
   ```

---

## Scaling

### Vertical Scaling (Increase Resources)

#### API Service

```bash
# Increase memory
terraform apply -var-file=envs/prod/terraform.tfvars \
  -var="api_memory=1Gi"

# Cloud Run automatically allocates more CPU with more memory
```

#### Orders Listener Function

```bash
# Increase function memory
terraform apply -var-file=envs/prod/terraform.tfvars \
  -var="function_memory=512"
```

### Horizontal Scaling (Increase Instances)

#### API Service

```bash
# Increase minimum and maximum replicas
terraform apply -var-file=envs/prod/terraform.tfvars \
  -var="api_replicas=5"

# Or scale manually via gcloud
gcloud run services update api --min-instances=2 --max-instances=10 \
  --region us-central1
```

#### Orders Listener Function

- Cloud Functions auto-scales; configuration via Terraform:
  ```bash
  # Adjust concurrency (requests per instance)
  # Edit cloud_functions.tf and increase max_concurrency
  ```

### Database Scaling

Firestore auto-scales globally. Manual optimization:

1. **Create indexes** for complex queries:
   ```bash
   gcloud firestore indexes create --help
   ```

2. **Archive old data** to reduce storage costs:
   ```bash
   # Implement data retention policy
   # Move orders > 2 years to Cloud Storage Archive
   ```

---

## Backup & Disaster Recovery

### Firestore Backups

Firestore backups are automatic (30+ day retention).

**Manual backup:**
```bash
gcloud firestore databases backup create \
  --retention=7d \
  --database=default
```

**List backups:**
```bash
gcloud firestore databases backups list
```

**Restore from backup:**
```bash
gcloud firestore databases restore PROJECT_ID DATABASE_ID BACKUP_ID
```

### Cloud Storage Backups

Terraform state stored in GCS with auto-versioning:

```bash
# Enable versioning (if not already)
gsutil versioning set on gs://jamble-terraform-state

# List versions
gsutil ls -L gs://jamble-terraform-state/terraform/state/

# Restore from version
gsutil cp gs://jamble-terraform-state/terraform/state/default.tfstate#<version> \
  terraform.tfstate
```

### Code Backups

Repository acts as code backup. Branch strategy:

- `main` – Production-ready code
- `develop` – Development branch
- `feature/*` – Feature branches

Tag releases:
```bash
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0
```

### Disaster Recovery Procedure

**Scenario: Database corrupted or accidentally deleted**

1. **Stop applications** to prevent further writes:
   ```bash
   gcloud run services update api --no-traffic --region us-central1
   ```

2. **List available backups:**
   ```bash
   gcloud firestore databases backups list
   ```

3. **Restore to new database:**
   ```bash
   gcloud firestore databases restore PROJECT_ID DATABASE_ID BACKUP_ID
   ```

4. **Verify restored data:**
   ```bash
   gcloud firestore documents list --collection-id=Orders --limit=5
   ```

5. **Resume service:**
   ```bash
   gcloud run services update-traffic api --to-revisions LATEST=100 --region us-central1
   ```

---

## Known Issues

### Issue: Orders Listener doesn't trigger immediately

**Root Cause:** Polling interval (default 2 seconds) + Firestore eventual consistency

**Workaround:** 
- Orders typically arrive within 5-10 seconds
- Acceptable for non-real-time applications
- To reduce latency, decrease `BRIDGE_POLL_INTERVAL` in local.dev or implement Cloud Tasks for production

### Issue: Firestore emulator crashes during tests

**Root Cause:** Java memory exhaustion, concurrent test load

**Workaround:**
- Increase Java heap size:
  ```bash
  export JVM_OPTS="-Xmx4g"
  ```
- Reduce test parallelism:
  ```bash
  pytest -n 2  # Instead of auto
  ```

### Issue: Email sending fails with "Connection refused"

**Root Cause:** SMTP service not ready or credentials incorrect

**Workaround:**
- Verify MailHog/SendGrid config
- Check firewall/network policies
- Use mock SMTP for testing:
  ```bash
  export SMTP_MODE=mock  # In test environment
  ```

### Issue: "State lock held by another operation"

**Root Cause:** Another Terraform process is running

**Workaround:**
1. Wait for other process to complete
2. Force unlock (last resort):
   ```bash
   terraform force-unlock LOCK_ID
   ```

### Issue: Cloud Run cold starts slow

**Root Cause:** First request after deploy takes 10+ seconds

**Workaround:**
- Set minimum instances:
  ```bash
  gcloud run services update api \
    --min-instances=2 \
    --region us-central1
  ```

---

## Emergency Contacts & Escalation

| Issue | Contact | Escalation |
|-------|---------|-----------|
| GCP Quota exceeded | GCP Billing Support | Increase quota |
| Database corruption | On-call DBA | Restore from backup |
| API down > 5 min | Engineering Lead | Rollback deployment |
| Security incident | Security team | Follow incident response |
| Email service down | DevOps Engineer | Switch email provider |

---

## Checklists

### Pre-Production Deployment

- [ ] All tests passing (`make test`, `make test-integration`)
- [ ] Docker image built and pushed
- [ ] `orders_listener.zip` created (`make orders-fn-zip`)
- [ ] Terraform plan reviewed
- [ ] Environment variables configured correctly
- [ ] Database backups taken
- [ ] Load testing completed (optional)

### Post-Deployment Validation

- [ ] Health check passing (`/health` returns 200)
- [ ] User registration working
- [ ] Order placement working
- [ ] Email delivery verified
- [ ] Logs monitored for errors
- [ ] Alerting configured

### Incident Response

- [ ] Identify symptom
- [ ] Check logs immediately
- [ ] Isolate affected component
- [ ] Apply fix or rollback
- [ ] Verify recovery
- [ ] Document issue
- [ ] Post-mortem if P1/P2

---

## Next Steps

- Review [Terraform Documentation](terraform.md) for infrastructure details
- Check [API Documentation](api.md) for endpoint reference
- See [Local Development Guide](local-dev.md) for testing recommendations
