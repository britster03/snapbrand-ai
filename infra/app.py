#!/usr/bin/env python3
"""AWS CDK application entry point for imagifyy.ai infrastructure."""

import os

import aws_cdk as cdk

from snapbrand_stack import SnapBrandStack


app = cdk.App()

SnapBrandStack(
    app,
    "SnapBrandStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth() 