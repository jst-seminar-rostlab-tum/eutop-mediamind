variable "name" { type = string }

resource "aws_ecr_repository" "ecr" {
  name                 = var.name
  image_tag_mutability = "MUTABLE"
}

output "repository_url" {
  value = aws_ecr_repository.ecr.repository_url
}
