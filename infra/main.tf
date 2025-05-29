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

locals {
  secrets_arn = "arn:aws:secretsmanager:eu-central-1:313193269185:secret:mediamind/app-env-fUauFQ"
}

data "aws_vpc" "selected" {
  default = true
}

data "aws_secretsmanager_secret_version" "db_creds" {
  secret_id = local.secrets_arn
}

module "ecr" {
  source = "./modules/ecr"
  name   = "ecr-mediamind"
}

module "database" {
  source      = "./modules/database"
  db_name     = "mediamind"
  db_username = jsondecode(data.aws_secretsmanager_secret_version.db_creds.secret_string)["POSTGRES_USER"]
  db_password = jsondecode(data.aws_secretsmanager_secret_version.db_creds.secret_string)["POSTGRES_PASSWORD"]
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
  redis_endpoint  = module.redis.endpoint
  subnet_ids = [
    "subnet-02d92c593c836cd8c",
    "subnet-0906bc6f2f546aec8",
    "subnet-0825cd05d0b85c59d"
  ]
  vpc_id      = data.aws_vpc.selected.id
  secrets_arn = local.secrets_arn
}