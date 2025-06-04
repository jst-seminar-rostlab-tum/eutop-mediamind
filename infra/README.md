# Infra

This directory contains infrastructure-as-code and configuration files for deploying and managing our AWS resources.

## Usage

To deploy or update infrastructure:

0. Set Variables

```sh
touch infra/terraform.tfvars # Create a terraform.tfvars file if it doesn't exist.
echo 'db_username = "your_db_username"' >> infra/terraform.tfvars
echo 'db_password = "your_db_password"' >> infra/terraform.tfvars
```

1. Ensure you have the necessary AWS credentials configured.

```sh
cd infra
aws configure # Follow the prompts to enter your AWS Access Key, Secret Key, region, and output format.
terraform init # Initialize Terraform and download required providers.
```

2. Validate the configuration files and scripts.

```sh
terraform validate # Check the configuration for syntax errors and other issues.
```

3. Review the planned changes before applying them.

```sh
terraform plan # Show the changes that will be made to the infrastructure.
```

## Notes

- Find vpcId:

```sh
aws ec2 describe-vpcs --query "Vpcs[?IsDefault].VpcId" --output text
```

- Find subnetId:

```sh
aws ec2 describe-subnets --query "Subnets[?VpcId=='<vpcId>'].SubnetId" --output text
```

- Create secrets in AWS Secrets Manager:

```sh
aws secretsmanager create-secret \
  --name mediamind/app-env \
  --secret-string file://secrets.json
```

- Update secrets in AWS Secrets Manager:

```sh
aws secretsmanager update-secret \
  --secret-id mediamind/app-env \
  --secret-string file://secrets.json
```

- Get IP addr of ECS task:

  - Get ECS cluster name:

  ```sh
  aws ecs list-tasks --cluster mediamind-cluster
  ```

  - Get ENI ID of ECS task:

  ```sh
  aws ecs describe-tasks --cluster <cluster_name> --tasks <task_id>
  ```

- Short command to get private IP address of ECS task:

```sh
aws ecs describe-tasks \
  --cluster mediamind-cluster \
  --tasks <task_id> \
  --query "tasks[0].attachments[0].details[?name=='privateIPv4Address'].value" \
  --output text
```

- Short command to get public IP address of ECS task:

```sh
aws ecs describe-tasks \
  --cluster mediamind-cluster \
  --tasks <task_id> \
  --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" \
  --output text
```
```sh
aws ec2 describe-network-interfaces \
  --network-interface-ids <eni-id> \
  --query "NetworkInterfaces[0].Association.PublicIp" \
  --output text
```

- Get connection string for RDS:

```sh
aws rds describe-db-instances \
  --query "DBInstances[*].{Endpoint:Endpoint.Address,Port:Endpoint.Port,DBInstanceIdentifier:DBInstanceIdentifier}" \
  --output table
```

- Get connection string for Redis:

```sh
aws elasticache describe-cache-clusters \
  --cache-cluster-id <cache_cluster_name> \
  --query "CacheClusters[0].ConfigurationEndpoint.Address" \
  --output text
```

- Get connection string for Qdrant:

```sh
aws qdrant describe-collection \
  --collection-name <collection_name> \
  --query "collectionName" \
  --output text
```

- Manually push Docker image to ECR:

Replace `12345678910` with your AWS account ID and `mediamind-backend` with your Docker image name.

```sh
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 12345678910.dkr.ecr.eu-central-1.amazonaws.com

docker tag mediamind-backend:latest 12345678910.dkr.ecr.eu-central-1.amazonaws.com/mediamind-backend:latest

docker push 12345678910.dkr.ecr.eu-central-1.amazonaws.com/mediamind-backend:latest
```
