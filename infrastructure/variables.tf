variable "region" {
    type = string
}

variable "location" {
    type = string
}

variable "project_id" {
    type = string
}

variable "kms_encryption" {
    type = string
    default = "rec-sys-vertex-ai"
}