variable "db_name" { type = string }
variable "db_username" { type = string }
variable "db_password" { type = string }

resource "aws_db_instance" "postgres" {
  allocated_storage         = 20
  engine                    = "postgres"
  engine_version            = "15"
  instance_class            = "db.t3.micro"
  db_name                   = var.db_name
  username                  = var.db_username
  password                  = var.db_password
  publicly_accessible       = true
  backup_retention_period   = 7
  backup_window             = "03:00-04:00"
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.db_name}-final-snapshot"
  delete_automated_backups  = false
}

output "endpoint" {
  value = aws_db_instance.postgres.endpoint
}
