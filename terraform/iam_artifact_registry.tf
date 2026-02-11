resource "google_artifact_registry_repository_iam_member" "run_reader" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.inventory.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.run_sa.email}"

  depends_on = [google_artifact_registry_repository.inventory]
}
