resource "google_service_account" "github_actions" {
  account_id   = "github-actions-sa"
  display_name = "GitHub Actions Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "github_actions_ar_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_service_account_key" "github_actions_key" {
  service_account_id = google_service_account.github_actions.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

output "github_actions_sa_key" {
  value       = base64decode(google_service_account_key.github_actions_key.private_key)
  sensitive   = true
  description = "Private key for GitHub Actions SA - add to GitHub Secrets as GCP_SA_KEY"
}

output "github_actions_sa_email" {
  value       = google_service_account.github_actions.email
  description = "GitHub Actions Service Account Email"
}
