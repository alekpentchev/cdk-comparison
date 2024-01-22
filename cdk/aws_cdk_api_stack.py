from aws_cdk import (
    Stack,
)
from constructs import Construct

from .network_stack import NetworkStack
from .api_stack import ApiStack
from .data_stack import DataStack

class AwsCdkApiStack(Stack):
    
    # AWS article on 3 tier web app
    # https://docs.aws.amazon.com/whitepapers/latest/serverless-multi-tier-architectures-api-gateway-lambda/presentation-tier.html

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

         # 3 tier web app divided into 4 stacks
        # 1. Network stack - public and private subnets
        self.network_stack = NetworkStack(self, 'network')
        # 2. Data stack - DynamoDB table
        self.data_stack = DataStack(self, 'data', self.network_stack.vpc)
        # 3. API stack - API Gateway and Lambda
        self.api_stack = ApiStack(self, 'api', self.network_stack.vpc, self.data_stack.dynamodb_table)
