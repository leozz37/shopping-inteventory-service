variable "project_id" { type = string }
variable "region"     { 
    type = string  
    default = "us-central1"
}
variable "app_name"   { 
    type = string  
    default = "orders-api" 
}

# Image URI to deploy Cloud Run (you build/push it via gcloud)
variable "cloud_run_image" { type = string }

# Mail provider settings (put secrets in Secret Manager in a real take-home)
variable "mail_provider_base_url" { type = string }
variable "mail_provider_api_key"  { 
    type = string 
    sensitive = true
}