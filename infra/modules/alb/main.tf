variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "certificate_arn_prod" { type = string }
variable "certificate_arn_dev" { type = string }
variable "certificate_arn_qdrant" { type = string }

resource "aws_security_group" "alb" {
  name_prefix = "mediamind-alb-sg-"
  description = "Allow HTTP/HTTPS"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "shared" {
  name               = "mediamind-shared-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.shared.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn_prod

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Not found"
      status_code  = "404"
    }
  }
}

resource "aws_lb_listener_certificate" "dev" {
  listener_arn    = aws_lb_listener.https.arn
  certificate_arn = var.certificate_arn_dev
}

resource "aws_lb_listener_certificate" "qdrant" {
  listener_arn    = aws_lb_listener.https.arn
  certificate_arn = var.certificate_arn_qdrant
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.shared.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_target_group" "prod" {
  name        = "mediamind-prod-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check {
    protocol = "HTTP"
    path     = "/api/v1/healthcheck"
    port     = "8000"
  }
}

resource "aws_lb_target_group" "dev" {
  name        = "mediamind-dev-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check {
    protocol = "HTTP"
    path     = "/api/v1/healthcheck"
    port     = "8000"
  }
}

resource "aws_lb_target_group" "qdrant" {
  name        = "mediamind-qdrant-tg"
  port        = 6333
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check {
    protocol = "HTTP"
    path     = "/"
    port     = "6333"
  }
}

resource "aws_lb_listener_rule" "prod" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.prod.arn
  }
  condition {
    host_header {
      values = ["api.mediamind.csee.tech"]
    }
  }
}

resource "aws_lb_listener_rule" "dev" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 20
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.dev.arn
  }
  condition {
    host_header {
      values = ["dev.api.mediamind.csee.tech"]
    }
  }
}

resource "aws_lb_listener_rule" "qdrant" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 30
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.qdrant.arn
  }
  condition {
    host_header {
      values = ["qdrant.api.mediamind.csee.tech"]
    }
  }
}

output "alb_security_group_id" {
  value = aws_security_group.alb.id
}

output "alb_arn" {
  value = aws_lb.shared.arn
}

output "alb_dns_name" {
  value = aws_lb.shared.dns_name
}

output "alb_listener_arn" {
  value = aws_lb_listener.https.arn
}

output "alb_target_group_arn_prod" {
  value = aws_lb_target_group.prod.arn
}

output "alb_target_group_arn_dev" {
  value = aws_lb_target_group.dev.arn
}

output "alb_target_group_arn_qdrant" {
  value = aws_lb_target_group.qdrant.arn
}
