resource "google_service_account" "run_sa" {
  account_id   = "${var.app_name}-run-sa"
  display_name = "Cloud Run SA for ${var.app_name}"
}

resource "google_cloud_run_v2_service" "app" {
  name     = var.app_name
  location = var.region

  template {
    service_account = google_service_account.run_sa.email
    containers {
      image = var.cloud_run_image
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Public access (optional). Remove if you want auth-only.
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.app.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
