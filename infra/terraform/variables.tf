variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "us-central1"
}
variable "app_name" {
  type    = string
  default = "orders-api"
}

variable "jwt_secret_value" {
  type        = string
  description = "JWT signing secret (store outside git)."
  sensitive   = true
}

variable "jwt_expires_minutes" {
  type        = number
  description = "Access token expiration in minutes"
  default     = 60
}

variable "api_image" {
  type = string
}

variable "mail_provider_base_url" {
  type = string
}

variable "mail_provider_api_key" {
  type      = string
  sensitive = true
}