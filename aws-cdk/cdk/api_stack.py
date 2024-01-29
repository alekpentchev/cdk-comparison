from aws_cdk import (
    Stack,
)
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigateway
import aws_cdk.aws_iam as iam
from aws_cdk.aws_lambda import IFunction
from constructs import Construct

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc, dynamoDBTable, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Lambda function to get list of medicines
        # should be in private subnet
        # should connect to DynamoDb with GatewayVpcEndpoint
        self.lambda_func = _lambda.Function(self, "Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_api.handler",
            code=_lambda.Code.from_asset("functions/lambda_api"),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            environment={
                'TABLE_NAME': dynamoDBTable.table_name
            }
        )
                
        # Allow Lambda to read from DynamoDB
        dynamoDBTable.grant_read_data(self.lambda_func)
        
        # API Gateway
        # should be in public subnet
        # should connect to Lambda with VpcLink
        self.api_gateway = apigateway.RestApi(self, "API",
            rest_api_name="Medicine Service",
            description="This service serves medicines.",
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True
            )
        )
        
        # API Gateway integration with Lambda
        # ERROR: strange type error for handler expecting IFunction and getting Function
        self.api_gateway_integration = apigateway.LambdaIntegration(
            handler=self.lambda_func, # type: ignore # cdk synths correctly
            proxy=False,
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Credentials': "'true'"
                }
            }]
        )
        
        # API Gateway method
        self.api_gateway_resource = self.api_gateway.root.add_resource("medicine")
        self.api_gateway_method = self.api_gateway_resource.add_method("GET",
            self.api_gateway_integration,
            request_parameters={
                'method.request.querystring.name': True
            }
        )
        
        # API Gateway method response
        self.api_gateway_method_response = self.api_gateway_method.add_method_response(
            status_code='200',
            response_parameters={
                'method.response.header.Access-Control-Allow-Origin': True,
                'method.response.header.Access-Control-Allow-Credentials': True
            }
        )
        
        # Allow only API Gateway to invoke Lambda
        self.lambda_func.add_permission("Permission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=self.api_gateway.arn_for_execute_api()
        )
