from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import (
    Tags,
)

from cdk.stack_apigw_auth import ApigwAuthStack

app = cdk.App()
apigw_stack = ApigwAuthStack(
    app, app.node.try_get_context("project_name"))
Tags.of(apigw_stack).add("Project", app.node.try_get_context("project_name"))
Tags.of(apigw_stack).add("Type", "test")
Tags.of(apigw_stack).add("Creator", "cdk")
app.synth()
