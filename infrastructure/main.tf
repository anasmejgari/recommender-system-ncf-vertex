terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region = var.region
}

module "vertex_ai" {
  source = "./modules/vertex_ai"
  project_id = var.project_id
  region     = var.region
  location   = var.location
  kms_encryption = var.kms_encryption
}

module "cloud_run" {
  source = "./modules/cloud_run"
}

module "artifact_registry" {
  source = "./modules/artifact_registry"
}
