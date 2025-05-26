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

4. Apply the changes to provision or update the infrastructure.

```sh
terraform apply # Apply the planned changes to the AWS infrastructure.
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
