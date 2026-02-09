resource "google_service_account" "fn_sa" {
  account_id   = "orders-listener-fn-sa"
  display_name = "Cloud Function SA for orders listener"
}

# Permissions: read Firestore + write logs (add Secret Manager if used)
resource "google_project_iam_member" "fn_firestore_user" {
  project = var.project_id
  role   = "roles/datastore.user"
  member = "serviceAccount:${google_service_account.fn_sa.email}"
}

resource "google_cloudfunctions2_function" "orders_listener" {
  name     = "orders-listener"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "on_order_created"
    source {
      storage_source {
        bucket = google_storage_bucket.fn_source.name
        object = google_storage_bucket_object.fn_zip.name
      }
    }
  }

  service_config {
    service_account_email = google_service_account.fn_sa.email
    environment_variables = {
      MAIL_PROVIDER_BASE_URL = var.mail_provider_base_url
      MAIL_PROVIDER_API_KEY  = var.mail_provider_api_key
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.firestore.document.v1.created"
    event_filters {
      attribute = "document"
      value     = "projects/${var.project_id}/databases/(default)/documents/orders/{orderId}"
    }
  }

  depends_on = [google_project_service.apis, google_firestore_database.default]
}

# Bucket/object to upload function source (zip)
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
