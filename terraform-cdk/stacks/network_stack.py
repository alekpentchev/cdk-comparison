#!/usr/bin/env python
from cdktf_cdktf_provider_aws.provider import AwsProvider
from constructs import Construct
from cdktf import TerraformStack
from imports.vpc import Vpc
from imports.aws.subnet import Subnet
from imports.aws.route_table import RouteTable
from imports.aws.route_table_association import RouteTableAssociation


class NetworkStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, prefix: str, **kwargs):
        super().__init__(scope, id)

        AwsProvider(self, "AWS",
                    region="eu-central-1",
                    shared_config_files=["~/.aws/config", "~/.aws/credentials"],
                    shared_credentials_files=["~/.aws/credentials"],
                    profile="alek",
                    )

        self.vpc = Vpc(self, f'{prefix}-vpc', name=f'{prefix}-vpc',
            azs = ['eu-central-1a', 'eu-central-1b', 'eu-central-1c'],
            default_security_group_egress=[
                {
                    "from_port":"0",
                    "to_port": "0",
                    "protocol": "-1",
                    "cidr_blocks": "0.0.0.0/0"
                }
            ]
        )

        subnet_config = [
            {"cidr_block": "10.0.1.0/24", "availability_zone": "eu-central-1a"},
            {"cidr_block": "10.0.2.0/24", "availability_zone": "eu-central-1b"},
            {"cidr_block": "10.0.3.0/24", "availability_zone": "eu-central-1c"},
        ]

        self.route_table_ids = []

        for i, config in enumerate(subnet_config):
            subnet = Subnet(self, f"{prefix}subnet-{i + 1}",
                vpc_id=self.vpc.vpc_id_output,
                cidr_block=config["cidr_block"],
                availability_zone=config["availability_zone"],
            )

            # Create a route table and associate it with the subnet
            route_table = RouteTable(self, f"{prefix}-routetable-{i + 1}",
                vpc_id=self.vpc.vpc_id_output
            )

            RouteTableAssociation(self, f"{prefix}routetable-association-{i + 1}",
                subnet_id=subnet.id,
                route_table_id=route_table.id,
            )

            self.route_table_ids.append(route_table.id)
