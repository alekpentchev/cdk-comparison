#!/usr/bin/env python
import json


from constructs import Construct
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf import TerraformStack, TerraformResource
from cdktf_cdktf_provider_aws.dynamodb_table import DynamodbTable
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction, LambdaFunctionEnvironment
from cdktf_cdktf_provider_aws.iam_role import IamRole
from imports.vpc import Vpc
from imports.aws.vpc_endpoint import VpcEndpoint


class DataStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, network_stack):
        super().__init__(scope, id)

        vpc = network_stack.vpc


        AwsProvider(self, "AWS",
                    region="eu-central-1",
                    shared_config_files=["~/.aws/config", "~/.aws/credentials"],
                    shared_credentials_files=["~/.aws/credentials"],
                    profile="alek",
                    )


        # DynamoDB table containing list of medicines
        # table should be in private subnet
        self.dynamodb_table = DynamodbTable(
            self,
            id_=f'${id}-medicine',
            name='medicine',
            billing_mode='PAY_PER_REQUEST',
            hash_key='name',
            attribute=[
                {
                    "name": "name",
                    "type": "S"
                }
            ]
        )

        lambda_inline_policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "dynamodb:*"
                                ],
                                "Resource": [
                                    self.dynamodb_table.arn
                                ]
                            }
                        ]
                    }

        lambda_prefill_role = IamRole(
            self,
            id_=f'${id}-LambdaPrefillDynamoDBRole',
            name='LambdaPrefillDynamoDBRole',
            assume_role_policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}',
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            ],
            inline_policy=[
                {
                    "name": "DynamoDBReadWrite",
                    "policy": json.dumps(lambda_inline_policy)
                }
            ]
        )

        lambda_env_vars = LambdaFunctionEnvironment(variables={
            "TABLE_NAME": self.dynamodb_table.name
        })

        # Lambda function to prefill DynamoDB table with data
        lambda_prefill = LambdaFunction(
            self,
            id_=f'${id}-LambdaPrefillDynamoDB',
            function_name='LambdaPrefillDynamoDB',
            # TODO: fix the path somehow to be relative
            filename='/Users/pentcha1/Documents/private-projects/cdk-comparison-py/terraform-cdk/functions/lambda_prefill/lambda_prefill.py.zip',
            handler='lambda_prefill.handler',
            role=lambda_prefill_role.arn,
            runtime='python3.12',
            environment=lambda_env_vars
        )

        # Create a custom resource to invoke lambda function to prefill DynamoDB table while creating the stack
        prefill_lambda_resource = TerraformResource(
            self,
            id=f'${id}-LambdaPrefillCustomResource',
            terraform_resource_type='aws_lambda_invocation',
            depends_on=[self.dynamodb_table]
        )

        # Use add_override to provide specific Terraform configuration
        prefill_lambda_resource.add_override('function_name', lambda_prefill.function_name)
        # The argument "input" is required
        prefill_lambda_resource.add_override('input', '{}')

        # Configure DynamoDB endpoint in private subnet
        dynamo_db_endpoint = VpcEndpoint(
            self,
            id_=f'${id}-DynamoDbEndpoint',
            vpc_id=vpc.vpc_id_output,
            service_name='com.amazonaws.eu-central-1.dynamodb',
            vpc_endpoint_type='Gateway',
            depends_on=[self.dynamodb_table]
        )

        # Allow all principals to describe and list tables
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "dynamodb:DescribeTable",
                        "dynamodb:ListTables",
                        "dynamodb:Scan"
                    ],
                    "Resource": self.dynamodb_table.arn
                }
            ]
        }
        dynamo_db_endpoint.add_override('policy', json.dumps(policy))
