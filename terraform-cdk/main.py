#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS",
                    region="eu-central-1",
                    shared_config_files=["~/.aws/config", "~/.aws/credentials"],
                    shared_credentials_files=["~/.aws/credentials"],
                    profile="alek",
                    )

        bucket = S3Bucket(self, "terraform-cdk-bucket",
                          bucket="terraform-cdk-bucket",
                          )
        TerraformOutput(self, "bucket_name",
                        value=bucket.bucket,
                        )


app = App()
MyStack(app, "terraform-cdk")

app.synth()
