variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}

variable "environment" {
  description = "The environment name"
  type        = string
}

variable "location" {
  description = "The Google Cloud location"
  type        = string
}

variable "cloud_run_name_frontend" {
  description = "The name of the frontend Cloud Run service"
  type        = string
}

variable "gar_image_location_frontend" {
  description = "The location of the frontend container image in GAR"
  type        = string
}