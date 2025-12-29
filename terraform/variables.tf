variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "dental-backend"
}

variable "encryption_key" {
  description = "The Fernet encryption key for the app"
  type        = string
  sensitive   = true
}
