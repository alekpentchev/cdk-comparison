#!/usr/bin/env python
from cdktf import App
from cdktf_cdktf_provider_aws.provider import AwsProvider

from stacks.network_stack import NetworkStack
from stacks.data_stack import DataStack
from stacks.api_stack import ApiStack

app = App()

def main(app):
    AwsProvider(app, "AWS",
                region="eu-central-1",
                shared_config_files=["~/.aws/config", "~/.aws/credentials"],
                shared_credentials_files=["~/.aws/credentials"],
                profile="alek",
                )

    # web app divided into 3 stacks
    # 1. Network stack - public and private subnets
    network_stack = NetworkStack(app, 'terraform-network')
    # 2. Data stack - DynamoDB table
    data_stack = DataStack(app, 'terraform-data', network_stack)
    # 3. API stack - API Gateway and Lambda
    api_stack = ApiStack(app, 'terraform-api', network_stack, data_stack)

main(app)
app.synth()
