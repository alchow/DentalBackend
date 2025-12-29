terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Cloud SQL Instance
resource "google_sql_database_instance" "main" {
  name             = "${var.app_name}-db-${random_id.db_suffix.hex}"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false # For demo ease; set true in prod

  settings {
    tier = "db-f1-micro" # Smallest tier for dev
    
    # Allow Cloud Run to connect via Public IP (simplest for setup)
    # properly secured via IAM
    ip_configuration {
      ipv4_enabled = true 
    }
  }

  depends_on = [google_project_service.apis]
}

resource "random_id" "db_suffix" {
  byte_length = 4
}

# Database
resource "google_sql_database" "database" {
  name     = "dental_db"
  instance = google_sql_database_instance.main.name
}

# User
resource "random_password" "db_password" {
  length  = 16
  special = false
}

resource "google_sql_user" "users" {
  name     = "dental_user"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

# 3. Cloud Run Service Account
resource "google_service_account" "runner" {
  account_id   = "${var.app_name}-runner"
  display_name = "Cloud Run Service Account for ${var.app_name}"
}

# Grant Cloud SQL Client role
resource "google_project_iam_member" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.runner.email}"
}

# 4. Cloud Run Service
resource "google_cloud_run_service" "backend" {
  name     = var.app_name
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.runner.email
      
      containers {
        image = "gcr.io/${var.project_id}/${var.app_name}:latest"
        
        # Deploy env vars
        env {
          name  = "DB_TYPE"
          value = "postgres"
        }
        env {
          name  = "DB_USER"
          value = google_sql_user.users.name
        }
        env {
          name  = "DB_PASS"
          value = google_sql_user.users.password
        }
        env {
          name  = "DB_NAME"
          value = google_sql_database.database.name
        }
        env {
          name  = "INSTANCE_CONNECTION_NAME"
          value = google_sql_database_instance.main.connection_name
        }
        # Using the instance connection name is key for the Cloud SQL Auth Proxy built-in to Cloud Run
        env {
           name = "DB_HOST"
           value = "/cloudsql/${google_sql_database_instance.main.connection_name}"
        }
         env {
           name = "ENCRYPTION_KEY"
           value = var.encryption_key
        }
      }
    }
    
    metadata {
      annotations = {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main.connection_name
        "run.googleapis.com/client-name"        = "terraform"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.apis, google_project_iam_member.sql_client]
}

# Allow public access
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
