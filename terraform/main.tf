terraform {
  backend "gcs" {
    bucket = "shopping-inventory-service-tf-state"
    prefix = "dev"
  }
}
