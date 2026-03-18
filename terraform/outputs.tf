output "api_url" {
  description = "URL pública da sua API"
  value       = google_cloud_run_v2_service.genetic_route_optimizer_api.uri
}