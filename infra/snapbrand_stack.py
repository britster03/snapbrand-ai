from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import (
    aws_apprunner as apprunner,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_s3 as s3,
    Duration,
    RemovalPolicy,
)
from constructs import Construct


class SnapBrandStack(cdk.Stack):
    """Infrastructure stack for imagifyy.ai."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs):  # type: ignore[override]
        super().__init__(scope, construct_id, **kwargs)

        # ------------------------------------------------------------------
        # S3 bucket for generated & brand assets
        # ------------------------------------------------------------------
        bucket = s3.Bucket(
            self,
            "AssetsBucket",
            versioned=True,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="expire-previous-versions", noncurrent_version_expiration=Duration.days(30)
                )
            ],
        )

        # ------------------------------------------------------------------
        # ECR repository to store backend container
        # ------------------------------------------------------------------
        repository = ecr.Repository(
            self,
            "BackendRepo",
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # ------------------------------------------------------------------
        # IAM role for App Runner with Bedrock & S3 access
        # ------------------------------------------------------------------
        runner_role = iam.Role(
            self,
            "AppRunnerTaskRole",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
        )

        bucket.grant_read_write(runner_role)

        # Grant Bedrock invoke permission
        runner_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                resources=["*"],
            )
        )

        # ------------------------------------------------------------------
        # App Runner service definition
        # ------------------------------------------------------------------
        apprunner_service = apprunner.CfnService(
            self,
            "BackendAppRunner",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=runner_role.role_arn
                ),
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=f"{repository.repository_uri}:latest",
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8000",
                        runtime_environment_variables=[
                            apprunner.CfnService.KeyValuePairProperty(
                                name="S3_BUCKET_NAME", value=bucket.bucket_name
                            )
                        ],
                    ),
                ),
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                path="/health",
                healthy_threshold=3,
                unhealthy_threshold=5,
                interval=Duration.seconds(10).to_seconds(),
                timeout=Duration.seconds(5).to_seconds(),
            ),
        )

        cdk.CfnOutput(self, "AssetsBucketName", value=bucket.bucket_name)
        cdk.CfnOutput(
            self, "AppRunnerServiceUrl", value=apprunner_service.attr_service_url
        ) 