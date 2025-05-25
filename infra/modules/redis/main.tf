variable "name" { type = string }

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = var.name
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
}

output "endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}