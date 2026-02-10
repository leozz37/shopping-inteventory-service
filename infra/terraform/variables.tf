variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "us-central1"
}
variable "app_name" {
  type    = string
  default = "orders-api"
}

variable "api_image" {
  type = string
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

variable "SMTP_HOST" {
  type = string
}

variable "SMTP_PORT" {
  type = string
}

variable "SMTP_USER" {
  type = string
}

variable "SMTP_FROM" {
  type = string
}

variable "SMTP_USE_TLS" {
  type = string
}

variable "SMTP_PASSWORD" {
  type      = string
}
