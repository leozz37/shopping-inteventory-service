resource "google_service_account" "fn_sa" {
  account_id   = "orders-listener-fn-sa"
  display_name = "Cloud Function SA for orders listener"
}

resource "google_project_iam_member" "fn_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.fn_sa.email}"
}

resource "google_cloudfunctions_function" "orders_listener" {
  name        = "orders-listener"
  runtime     = "python312"
  region      = var.region
  entry_point = "orders_listener"

  source_archive_bucket = google_storage_bucket.fn_source.name
  source_archive_object = google_storage_bucket_object.fn_zip.name

  event_trigger {
    event_type = "providers/cloud.firestore/eventTypes/document.create"
    resource   = "projects/${var.project_id}/databases/(default)/documents/Orders/{orderId}"
  }

  environment_variables = {
    SMTP_HOST     = var.SMTP_HOST
    SMTP_PORT     = var.SMTP_PORT
    SMTP_USER     = var.SMTP_USER
    SMTP_FROM     = var.SMTP_FROM
    SMTP_USE_TLS  = var.SMTP_USE_TLS
    SMTP_PASSWORD = var.SMTP_PASSWORD
  }

  service_account_email = google_service_account.fn_sa.email
}

resource "google_storage_bucket" "fn_source" {
  name                        = "${var.project_id}-fn-source-${var.region}"
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "fn_zip" {
  name   = "orders_listener.zip"
  bucket = google_storage_bucket.fn_source.name
  source = "${path.module}/../..//dist/orders_listener.zip"
}
