resource "google_service_account" "run_sa" {
  account_id   = "${var.app_name}-run-sa"
  display_name = "Cloud Run SA for ${var.app_name}"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "inventory-api"
  location = var.region

  template {
    service_account = google_service_account.run_sa.email

    containers {
      image = var.api_image

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "JWT_EXPIRES_MINUTES"
        value = tostring(var.jwt_expires_minutes)
      }

      env {
        name = "JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt_secret.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "JWT_ALGORITHM"
        value = "HS256"
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
