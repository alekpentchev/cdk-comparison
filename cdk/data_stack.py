from aws_cdk import (
    RemovalPolicy,
    Stack
)
from aws_cdk.aws_dynamodb import (Table, Attribute, AttributeType)
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
from constructs import Construct

class DataStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB table containing list of medicines
        # table should be in private subnet
        self.dynamodb_table = Table(
            self, 'medicine',
            partition_key=Attribute(
                name='name',
                type=AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        
        # Configure DynamoDB endpoint in private subnet
        self.dynamo_db_endpoint = vpc.add_gateway_endpoint("DynamoDbEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB
        )
        # Allow all principals to describe and list tables
        self.dynamo_db_endpoint.add_to_policy(
            iam.PolicyStatement( # Restrict to listing and describing tables
                principals=[iam.AnyPrincipal()],
                actions=["dynamodb:DescribeTable", "dynamodb:ListTables", "dynamodb:Scan"],
                resources=[self.dynamodb_table.table_arn]))