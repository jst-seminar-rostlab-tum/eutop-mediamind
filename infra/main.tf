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
  secrets_arn  = "arn:aws:secretsmanager:eu-central-1:313193269185:secret:mediamind/app-env-fUauFQ"
  cluster_name = "mediamind-cluster"
}

data "aws_vpc" "selected" {
  default = true
}

data "aws_subnets" "selected" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

data "aws_secretsmanager_secret_version" "creds" {
  secret_id = local.secrets_arn
}

module "ecr" {
  source = "./modules/ecr"
  name   = "ecr-mediamind"
}

module "database" {
  source      = "./modules/database"
  db_name     = "mediamind"
  db_username = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)["POSTGRES_USER"]
  db_password = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)["POSTGRES_PASSWORD"]
}

module "redis" {
  source = "./modules/redis"
  name   = "mediamind-redis"
}

module "ecs" {
  source          = "./modules/ecs"
  service_name    = "mediamind-service"
  cluster_name    = local.cluster_name
  container_image = module.ecr.repository_url
  db_endpoint     = module.database.endpoint
  redis_endpoint  = module.redis.endpoint
  subnet_ids      = data.aws_subnets.selected.ids
  vpc_id          = data.aws_vpc.selected.id
  secrets_arn     = local.secrets_arn
}

module "qdrant" {
  source         = "./modules/qdrant"
  service_name   = "mediamind"
  cluster_name   = local.cluster_name
  subnet_ids     = data.aws_subnets.selected.ids
  vpc_id         = data.aws_vpc.selected.id
  vpc_cidr_block = data.aws_vpc.selected.cidr_block
  api_key        = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)["QDRANT_API_KEY"]
}
