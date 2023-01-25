import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    Duration,
)
from constructs import Construct


class ApigwAuthStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        auth_table = dynamodb.Table(
            self, "table",
            table_name="dyn-apigw-auth-usr-cdk",
            partition_key=dynamodb.Attribute(
                name="key",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        usr_fn = _lambda.Function(
            self,
            "usr_fn",
            function_name="lmd-apigw-auth-usr-cdk",
            code=_lambda.Code.from_asset("src/usr"),
            handler="lambda_function.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(3),
            memory_size=128,
        )

        auth_fn = _lambda.Function(
            self,
            "auth_fn",
            function_name="lmd-apigw-auth-auth-cdk",
            code=_lambda.Code.from_asset("src/auth"),
            handler="lambda_function.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(3),
            memory_size=128,
        )
        auth_fn.add_environment("REGION", cdk.Aws.REGION)
        auth_fn.add_environment("ACCOUNT_ID", cdk.Aws.ACCOUNT_ID)
        auth_fn.add_environment("TABLE_NAME", auth_table.table_name)
        auth_table.grant_read_data(auth_fn.role)  # type: ignore

        auth = apigateway.TokenAuthorizer(
            self,
            "auth",
            handler=auth_fn,
            authorizer_name="apigw-auth-sample",
        )

        api = apigateway.RestApi(
            self,
            "api",
            rest_api_name="apigw-auth-sample",
            deploy_options=apigateway.StageOptions(
                data_trace_enabled=True,
                logging_level=apigateway.MethodLoggingLevel.INFO,
            )
        )
        usr = api.root.add_resource("usr")
        usr_id = usr.add_resource("{id}")
        usr_id.add_method(
            "POST",
            integration=apigateway.LambdaIntegration(usr_fn),
            authorizer=auth,
        )
