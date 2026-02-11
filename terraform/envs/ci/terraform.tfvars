# project
project_id = "dummy-project-id"
region     = "us-central1"

# Cloud Run
app_name  = "inventory-api"
api_image = "gcr.io/dummy-project-id/inventory-api:ci"

# JWT
jwt_expires_minutes = 60

# Mail (Cloud Function)
mail_provider_base_url = "https://example.invalid"
