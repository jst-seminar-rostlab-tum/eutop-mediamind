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
  secrets_arn     = "arn:aws:secretsmanager:eu-central-1:313193269185:secret:mediamind/app-env-fUauFQ"
  dev_secrets_arn = "arn:aws:secretsmanager:eu-central-1:313193269185:secret:mediamind/dev-env-mjm2wi"
  cluster_name    = "mediamind-cluster"
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

data "aws_secretsmanager_secret_version" "dev_creds" {
  secret_id = local.dev_secrets_arn
}

module "ecr" {
  source = "./modules/ecr"
  name   = "ecr-mediamind"
}

module "ecr_scheduler" {
  source = "./modules/ecr"
  name   = "ecr-mediamind-scheduler"
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

module "s3" {
  source = "./modules/s3"
  name   = "eutop-mediamind"
}

module "alb" {
  source                 = "./modules/alb"
  vpc_id                 = data.aws_vpc.selected.id
  subnet_ids             = data.aws_subnets.selected.ids
  certificate_arn_prod   = "arn:aws:acm:eu-central-1:313193269185:certificate/ba1c0b9b-2c80-4c0f-acf6-355dfb9ba658"
  certificate_arn_dev    = "arn:aws:acm:eu-central-1:313193269185:certificate/3f5b9917-f56f-414a-ab56-b751c55733ee"
  certificate_arn_qdrant = "arn:aws:acm:eu-central-1:313193269185:certificate/3f5b9917-f56f-414a-ab56-b751c55733ee"
}

module "ecs" {
  source                = "./modules/ecs"
  service_name          = "mediamind-service"
  cluster_name          = local.cluster_name
  container_image       = module.ecr.repository_url
  db_endpoint           = module.database.endpoint
  redis_endpoint        = module.redis.endpoint
  subnet_ids            = data.aws_subnets.selected.ids
  vpc_id                = data.aws_vpc.selected.id
  secrets_arn           = local.secrets_arn
  s3_backend_bucket     = module.s3.bucket
  region                = "eu-central-1"
  alb_target_group_arn  = module.alb.alb_target_group_arn_prod
  alb_listener_arn      = module.alb.alb_listener_arn
  alb_security_group_id = module.alb.alb_security_group_id
  cpu                   = "2048"
  memory                = "4096"
}

module "ecs_dev" {
  source                = "./modules/ecs"
  service_name          = "mediamind-service-dev"
  cluster_name          = local.cluster_name
  container_image       = module.ecr.repository_url
  db_endpoint           = module.database.endpoint
  redis_endpoint        = module.redis.endpoint
  subnet_ids            = data.aws_subnets.selected.ids
  vpc_id                = data.aws_vpc.selected.id
  secrets_arn           = local.dev_secrets_arn
  s3_backend_bucket     = module.s3.bucket
  region                = "eu-central-1"
  alb_target_group_arn  = module.alb.alb_target_group_arn_dev
  alb_listener_arn      = module.alb.alb_listener_arn
  alb_security_group_id = module.alb.alb_security_group_id
  cpu                   = "256"
  memory                = "1024"
}

module "scheduler" {
  source                     = "./modules/scheduler"
  service_name               = "mediamind-scheduler"
  cluster_name               = local.cluster_name
  container_image            = module.ecr_scheduler.repository_url
  redis_endpoint             = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)["REDIS_URL"]
  api_base_url               = "https://api.mediamind.csee.tech/api"
  pipeline_morning_time      = "5:00"
  pipeline_afternoon_time    = "12:00"
  pipeline_evening_time      = "18:00"
  email_job_interval         = "3600"
  rss_job_interval           = "1800"
  breaking_news_job_interval = "3600"
  subnet_ids                 = data.aws_subnets.selected.ids
  vpc_id                     = data.aws_vpc.selected.id
  region                     = "eu-central-1"
}

module "scheduler_dev" {
  source                     = "./modules/scheduler"
  service_name               = "mediamind-scheduler-dev"
  cluster_name               = local.cluster_name
  container_image            = module.ecr_scheduler.repository_url
  redis_endpoint             = jsondecode(data.aws_secretsmanager_secret_version.dev_creds.secret_string)["REDIS_URL"]
  api_base_url               = "https://dev.api.mediamind.csee.tech/api"
  pipeline_morning_time      = ""
  pipeline_afternoon_time    = ""
  pipeline_evening_time      = ""
  email_job_interval         = "-1"
  rss_job_interval           = "-1"
  breaking_news_job_interval = "-1"
  subnet_ids                 = data.aws_subnets.selected.ids
  vpc_id                     = data.aws_vpc.selected.id
  region                     = "eu-central-1"
}

module "qdrant" {
  source                = "./modules/qdrant"
  service_name          = "mediamind"
  cluster_name          = local.cluster_name
  subnet_ids            = data.aws_subnets.selected.ids
  vpc_id                = data.aws_vpc.selected.id
  vpc_cidr_block        = data.aws_vpc.selected.cidr_block
  api_key               = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)["QDRANT_API_KEY"]
  alb_target_group_arn  = module.alb.alb_target_group_arn_qdrant
  alb_listener_arn      = module.alb.alb_listener_arn
  alb_security_group_id = module.alb.alb_security_group_id
}
