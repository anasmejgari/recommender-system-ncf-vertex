resource "google_vertex_ai_featurestore" "recommender_featurestore" {
  name     = "recommender-featurestore"
  region   = var.region
  project  = var.project_id
  online_serving_config {
    fixed_node_count = 1
    # scaling {
    #     min_node_count = 1
    #     max_node_count = 2
    # }
  }
  encryption_spec {
    kms_key_name = var.kms_encryption
  }
}

resource "random_integer" "random_endpoint" {
  min = 1
  max = 50000
}

resource "google_vertex_ai_endpoint" "endpoint" {
  name         = "recommender-endpoint-${random_integer.random_endpoint}"
  display_name = "recommender-vertex-ai-endpoint"
  description  = "A vertex endpoint for NCF Recommender System"
  location     = var.location
  region       = var.region
}

