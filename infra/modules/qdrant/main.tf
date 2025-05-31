variable "service_name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_id" { type = string }
variable "cluster_name" { type = string }
variable "vpc_cidr_block" { type = string }
variable "api_key" { type = string }

resource "aws_security_group" "qdrant" {
  name_prefix = "${var.service_name}-qdrant-sg-"
  description = "Allow inbound traffic to Qdrant"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6333
    to_port     = 6333
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "qdrant_task_execution_role" {
  name               = "${var.service_name}-qdrant-task-execution"
  assume_role_policy = data.aws_iam_policy_document.qdrant_task_assume_role_policy.json
}

data "aws_iam_policy_document" "qdrant_task_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "qdrant_task_execution_role_policy" {
  role       = aws_iam_role.qdrant_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_efs_file_system" "qdrant" {
  creation_token = "${var.service_name}-qdrant-efs"
  lifecycle_policy {
    transition_to_ia = "AFTER_7_DAYS"
  }
}

resource "aws_efs_mount_target" "qdrant" {
  for_each        = toset(var.subnet_ids)
  file_system_id  = aws_efs_file_system.qdrant.id
  subnet_id       = each.value
  security_groups = [aws_security_group.qdrant.id]
}

resource "aws_ecs_task_definition" "qdrant" {
  family                   = "${var.service_name}-qdrant"
  execution_role_arn       = aws_iam_role.qdrant_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  volume {
    name = "qdrant-data"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.qdrant.id
      transit_encryption = "ENABLED"
      root_directory     = "/"
    }
  }
  container_definitions = jsonencode([
    {
      name         = "qdrant"
      image        = "qdrant/qdrant:latest"
      essential    = true
      portMappings = [{ containerPort = 6333 }]
      mountPoints = [{
        sourceVolume  = "qdrant-data"
        containerPath = "/qdrant/storage"
        readOnly      = false
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.service_name}-qdrant"
          awslogs-region        = "eu-central-1"
          awslogs-stream-prefix = "qdrant"
        }
      }
      environment = [
        {
          name  = "QDRANT__SERVICE__API_KEY"
          value = var.api_key
        }
      ]
    }
  ])
}

resource "aws_cloudwatch_log_group" "qdrant" {
  name              = "/ecs/${var.service_name}-qdrant"
  retention_in_days = 7
}

resource "aws_ecs_service" "qdrant" {
  name            = "${var.service_name}-qdrant"
  cluster         = var.cluster_name
  task_definition = aws_ecs_task_definition.qdrant.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = true
    security_groups  = [aws_security_group.qdrant.id]
  }
  depends_on = [aws_cloudwatch_log_group.qdrant]
}

output "qdrant_service_name" {
  value = aws_ecs_service.qdrant.name
}
