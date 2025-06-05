variable "name" { type = string }

resource "aws_s3_bucket" "backend" {
  bucket        = var.name
  force_destroy = true

  tags = {
    Name        = var.name
    Environment = terraform.workspace
  }
}

output "bucket" {
  value       = aws_s3_bucket.backend.bucket
  description = "The S3 bucket for Mediamind backend storage"
}
