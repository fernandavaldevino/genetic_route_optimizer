resource "google_cloud_run_v2_service" "genetic_route_optimizer_api" {
  name     = "genetic-route-optimizer-api"
  location = var.region

  template {
    timeout = "300s"
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    
    containers {
      image = var.image_url
      
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
        startup_cpu_boost = true
      }
    }
  }
}

# Permitir acesso público ao serviço
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.genetic_route_optimizer_api.name
  location = google_cloud_run_v2_service.genetic_route_optimizer_api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
