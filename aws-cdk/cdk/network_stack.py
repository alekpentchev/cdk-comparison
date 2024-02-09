from aws_cdk import (
    Stack,
)
import aws_cdk.aws_ec2 as ec2
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, prefix: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(self, f'{prefix}-vpc',
            max_azs=2,  # Adjust as needed
            subnet_configuration=[
                {
                    "cidrMask": 24,
                    "name": "PrivateSubnet",
                    "subnetType": ec2.SubnetType.PRIVATE_ISOLATED
                }
            ]
        )
