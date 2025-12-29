output "service_url" {
  value = google_cloud_run_service.backend.status[0].url
}

output "db_connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "db_password" {
  value     = random_password.db_password.result
  sensitive = true
}
