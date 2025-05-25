variable "db_name" { type = string }
variable "db_username" { type = string }
variable "db_password" { type = string }

resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  db_name              = var.db_name
  username             = var.db_username
  password             = var.db_password
  skip_final_snapshot  = true
  publicly_accessible  = false
}

output "endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "username" {
  value = var.db_username
}

output "password" {
  value = var.db_password
}