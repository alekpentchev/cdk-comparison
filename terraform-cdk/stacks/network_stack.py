#!/usr/bin/env python
from cdktf_cdktf_provider_aws.provider import AwsProvider
from constructs import Construct
from cdktf import TerraformStack
from imports.vpc import Vpc


class NetworkStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS",
                    region="eu-central-1",
                    shared_config_files=["~/.aws/config", "~/.aws/credentials"],
                    shared_credentials_files=["~/.aws/credentials"],
                    profile="alek",
                    )

        self.vpc = Vpc(self, "MyVPC",
            azs = ['eu-central-1a', 'eu-central-1b', 'eu-central-1c'],
            private_subnets = ['10.0.1.0/24', '10.0.2.0/24', '10.0.3.0/24'],
        )
