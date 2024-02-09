#!/usr/bin/env python
import json


from constructs import Construct
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf import TerraformStack, TerraformVariable
from imports.aws.api_gateway_rest_api import ApiGatewayRestApi
from cdktf_cdktf_provider_aws.api_gateway_integration import ApiGatewayIntegration
from cdktf_cdktf_provider_aws.api_gateway_resource import ApiGatewayResource
from cdktf_cdktf_provider_aws.api_gateway_method import ApiGatewayMethod
from cdktf_cdktf_provider_aws.api_gateway_method_response import ApiGatewayMethodResponse
from cdktf_cdktf_provider_aws.api_gateway_stage import ApiGatewayStage
from cdktf_cdktf_provider_aws.api_gateway_deployment import ApiGatewayDeployment
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction, LambdaFunctionVpcConfig, LambdaFunctionEnvironment
from cdktf_cdktf_provider_aws.iam_role import IamRole
from imports.aws.data_aws_subnets import DataAwsSubnets, DataAwsSubnetsFilter
from imports.aws.lambda_permission import LambdaPermission

class ApiStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, network_stack, data_stack, prefix: str):
        super().__init__(scope, id)

        account_id = "120732094208"
        my_region = "eu-central-1"

        vpc = network_stack.vpc
        dynamoDBTable = data_stack.dynamodb_table

        AwsProvider(self, "AWS",
                    region="eu-central-1",
                    shared_config_files=["~/.aws/config", "~/.aws/credentials"],
                    shared_credentials_files=["~/.aws/credentials"],
                    profile="alek",
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
                                    dynamoDBTable.arn
                                ]
                            }
                        ]
                    }

         # Allow Lambda to read from DynamoDB
        lambda_role = IamRole(
            self,
            id_=f'${id}-LambdaRole',
            name=f'{prefix}-lambda-role',
            assume_role_policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}',
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
            ],
            inline_policy=[
                {
                    "name": "DynamoDBReadWrite",
                    "policy": json.dumps(lambda_inline_policy)
                }
            ]
        )

        subnet_ids = DataAwsSubnets(self, "vpc_subnet_ids",
            filter=[DataAwsSubnetsFilter(
                name="vpc-id",
                values=[vpc.vpc_id_output]
            )
            ]
        )
        subnet_ids = subnet_ids.ids

        lambda_func_vpc_config = LambdaFunctionVpcConfig(
            subnet_ids=subnet_ids,
            security_group_ids=[vpc.default_security_group_id_output]
        )

        lambda_env_vars = LambdaFunctionEnvironment(variables={
            "TABLE_NAME": dynamoDBTable.name
        })

        # Lambda function to get list of medicines
        # should be in private subnet
        # should connect to DynamoDb with GatewayVpcEndpoint
        lambda_func = LambdaFunction(
            self,
            id_=f'${id}-Function',
            function_name=f'{prefix}-lambda-api',
            role=lambda_role.arn,
            runtime='python3.12',
            handler='lambda_api.handler',
            timeout=30,
            # TODO: fix the path somehow to be relative
            filename='/Users/pentcha1/Documents/private-projects/cdk-comparison-py/terraform-cdk/functions/lambda_api/lambda_api.py.zip',
            vpc_config=lambda_func_vpc_config,
            environment=lambda_env_vars
        )

        # API Gateway
        # should be in public subnet
        # should connect to Lambda with VpcLink
        api_gateway = ApiGatewayRestApi(
            self,
            id_=f'${id}-API',
            name=f'{prefix}-api',
        )

        path_part = 'medicine'

        api_gateway_resource = ApiGatewayResource(
            self,
            id_=f'${id}-APIGatewayResource',
            rest_api_id=api_gateway.id,
            parent_id=api_gateway.root_resource_id,
            path_part=path_part
        )

        api_gateway_method = ApiGatewayMethod(
            self,
            id_=f'${id}-APIGatewayMethod',
            rest_api_id=api_gateway.id,
            resource_id=api_gateway_resource.id,
            http_method='GET',
            authorization='NONE'
        )

        LambdaPermission(self, "apigw_lambda",
            action="lambda:InvokeFunction",
            function_name=lambda_func.function_name,
            principal="apigateway.amazonaws.com",
            source_arn=f"arn:aws:execute-api:{my_region}:{account_id}:{api_gateway.id}/*/{api_gateway_method.http_method}/{path_part}",
            statement_id="AllowExecutionFromAPIGateway"
        )

        # API Gateway integration with Lambda
        api_gateway_integration = ApiGatewayIntegration(
            self,
            id_=f'${id}-APIGatewayIntegration',
            rest_api_id=api_gateway.id,
            resource_id=api_gateway_resource.id,
            http_method=api_gateway_method.http_method,
            integration_http_method="POST",
            type='AWS_PROXY',
            uri=lambda_func.invoke_arn,
        )

        # API Gateway method response
        ApiGatewayMethodResponse(
            self,
            id_=f'${id}-APIGatewayMethodResponse',
            rest_api_id=api_gateway.id,
            resource_id=api_gateway_resource.id,
            http_method='GET',
            status_code='200',
        )

        api_gateway_deployment = ApiGatewayDeployment(
            self,
            id_=f'${id}-APIGatewayDeployment',
            rest_api_id=api_gateway.id,
            description='Initial deployment',
            depends_on=[api_gateway_integration]
        )

        ApiGatewayStage(
            self,
            id_=f'${id}-APIGatewayStage',
            rest_api_id=api_gateway.id,
            deployment_id=api_gateway_deployment.id,
            stage_name='dev',
        )
