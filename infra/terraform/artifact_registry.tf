resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "containers"
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}
