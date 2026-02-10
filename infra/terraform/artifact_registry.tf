resource "google_artifact_registry_repository" "inventory" {
  project       = var.project_id
  location      = var.region
  repository_id = "inventory"
  format        = "DOCKER"

  depends_on = [google_project_service.artifactregistry]
}
