variable "cluster_name" { type = string }
variable "service_name" { type = string }
variable "container_image" { type = string }
variable "redis_endpoint" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_id" { type = string }
variable "region" { type = string }
variable "log_group_name" {
  type    = string
  default = null
}

locals {
  effective_log_group_name = var.log_group_name != null ? var.log_group_name : "/ecs/${var.service_name}"
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = local.effective_log_group_name
  retention_in_days = 7
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "${var.service_name}-ecs-task-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

data "aws_iam_policy_document" "ecs_task_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "app" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([
    {
      name      = var.service_name
      image     = var.container_image
      essential = true
      environment = [
        { name = "QUEUE_NAME", value = "default" },
        { name = "SCHEDULER_INTERVAL", value = "60" },
        { name = "EMAIL_JOB_INTERVAL", value = "30" },
        { name = "PIPELINE_JOB_INTERVAL", value = "1440" },
        { name = "REDIS_URL", value = var.redis_endpoint },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "app" {
  name            = var.service_name
  cluster         = var.cluster_name
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = false
  }
  depends_on = [aws_ecs_task_definition.app]
}
