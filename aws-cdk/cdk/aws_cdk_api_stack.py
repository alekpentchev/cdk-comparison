from aws_cdk import (
    Stack,
)
from constructs import Construct

from .network_stack import NetworkStack
from .api_stack import ApiStack
from .data_stack import DataStack

class AwsCdkApiStack(Stack):


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        prefix = "awscdk-"

        # web app divided into 3 stacks
        # 1. Network stack - public and private subnets
        self.network_stack = NetworkStack(self, prefix + 'network', prefix)
        # 2. Data stack - DynamoDB table
        self.data_stack = DataStack(self, prefix + 'data', self.network_stack.vpc, prefix)
        # 3. API stack - API Gateway and Lambda
        self.api_stack = ApiStack(self, prefix + 'api', self.network_stack.vpc, self.data_stack.dynamodb_table, prefix)
