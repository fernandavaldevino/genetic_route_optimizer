variable "project_id" {
  description = "ID do projeto no GCP"
  type        = string
  default     = "project-1804e3ce-8509-46cd-b62"
}

variable "region" {
  description = "Região onde os recursos serão criados"
  type        = string
  default     = "us-central1"
}

variable "image_url" {
  description = "URL da imagem Docker no Artifact Registry"
  type        = string
  default     = "us-central1-docker.pkg.dev/project-1804e3ce-8509-46cd-b62/gro-repository/genetic-route-optimizer-api@sha256:aa1993d6b2402224dd036d5348bdb7b953b2e38a69f114ef32085556cef7af9c"
}
