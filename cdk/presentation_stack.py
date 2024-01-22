from aws_cdk import (
    RemovalPolicy,
    Stack,
)
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_cloudfront as cloudfront
from constructs import Construct

class PresentationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 Bucket holding static website
        # should be in public subnet
        bucket = s3.Bucket(self, "Bucket",
            website_index_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # CloudFront distribution
        # should be in public subnet
        cloudfront_distro = cloudfront.CloudFrontWebDistribution(self, "CloudFront",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=bucket
                    ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)]
                )
            ]
        )
        
       # TODO: how to let CloudFront website access API Gateway?
    