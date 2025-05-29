terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "s3-mediamind-tfstate"
    key    = "terraform.tfstate"
    region = "eu-central-1"
  }
}

provider "aws" {
  region = "eu-central-1"
}

data "aws_vpc" "selected" {
  default = true
}

module "ecr" {
  source = "./modules/ecr"
  name   = "ecr-mediamind"
}

module "database" {
  source      = "./modules/database"
  db_name     = "mediamind"
  db_username = var.db_username
  db_password = var.db_password
}

module "redis" {
  source = "./modules/redis"
  name   = "mediamind-redis"
}

module "ecs" {
  source          = "./modules/ecs"
  cluster_name    = "mediamind-cluster"
  service_name    = "mediamind-service"
  container_image = module.ecr.repository_url
  db_endpoint     = module.database.endpoint
  db_username     = var.db_username
  db_password     = var.db_password
  redis_endpoint  = module.redis.endpoint
  subnet_ids = [
    "subnet-02d92c593c836cd8c",
    "subnet-0906bc6f2f546aec8",
    "subnet-0825cd05d0b85c59d"
  ]
  vpc_id = data.aws_vpc.selected.id
}