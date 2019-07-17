import boto3
import json
from os import path
from src.zip_utils import Utils
from pyspark import SparkContext


LAMBDA_ROLE = 'Lambda_Execution_Role'
LAMBDA_ACCESS_POLICY_ARN = 'arn:aws:iam::248516221011:policy/LambdaS3AccessPolicy'
LAMBDA_ROLE_ARN = 'arn:aws:iam::248516221011:role/Lambda_Execution_Role'
LAMBDA_TIMEOUT = 10
LAMBDA_MEMORY = 128
LAMBDA_HANDLER = 'lambda_function.handler'
PYTHON_RUNTIME = 'python3.7'
PYTHON_LAMBDA_NAME = 'PythonLambdaFuntion'


def lambda_client():
    aws_lambda = boto3.client('lambda', region_name='us-east-2')
    """:type : pyboto3.lambda """
    return aws_lambda


def iam_client():
    iam = boto3.client('iam')
    """:type : pyboto3.iam """
    return iam


def create_access_lambda():
    s3_access_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:*",
                    "logs:CreateLogGroup",
                    "logs:CreateLogsStream",
                    "logs:PutLogEvents"
                ],
                "Effect": "Allow",
                "Resource": "*"
            }
        ]
    }
    return iam_client().create_policy(
        PolicyName='LambdaS3AccessPolicy',
        PolicyDocument=json.dumps(s3_access_policy_document),
        Description='Allows lambda function to access s3'
    )


def create_execution_role_lambda():
    lambda_execution_assumption_role = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    return iam_client().create_role(
        RoleName=LAMBDA_ROLE,
        AssumeRolePolicyDocument=json.dumps(lambda_execution_assumption_role),
        Description='Gives Necessary Permissions for Lambda to be executed'
    )


def attach_access_policy_to_excution_role():
    return iam_client().attach_role_policy(
        RoleName=LAMBDA_ROLE,
        PolicyArn=LAMBDA_ACCESS_POLICY_ARN
    )


def deploy_lambda_function(function_name, runtime, handler, role_arn, source_path):
    folder_path = path.join(path.dirname(path.abspath(__file__)), source_path)
    zip_file = Utils.make_zip_file_bytes(folder_path)

    return lambda_client().create_function(
        FunctionName=function_name,
        Runtime=runtime,
        Role=role_arn,
        Handler=handler,
        Code={
            'ZipFile': zip_file
        },
        Timeout=LAMBDA_TIMEOUT,
        MemorySize=LAMBDA_MEMORY,
        Publish=False
    )


def invoke_lambda_function(function_name):
    return lambda_client().invoke(FunctionName=function_name)


def add_environment_variables_to_lambda(function_name, variables):
    return lambda_client().update_function_configuration(
        FunctionName=function_name,
        Environment=variables
    )


def update_lambda_function_code(function_name, source_path):
    folder_path = path.join(path.dirname(path.abspath(__file__)), source_path)
    zip_file = Utils.make_zip_file_bytes(folder_path)
    return lambda_client().update_function_code(
        FunctionName=function_name,
        ZipFile=zip_file
    )


def update_lambda_execution_memory(function_name, new_memory_size):
    return lambda_client().update_function_configuration(
        FunctionName=function_name,
        MemorySize=new_memory_size
    )


def publish_a_new_version(function_name):
    return lambda_client().publish_version(
        FunctionName=function_name
    )


def create_alias_for_new_version(function_name, alias_name, version):
    return lambda_client().create_alias(
        FunctionName=function_name,
        Name=alias_name,
        FunctionVersion=version,
        Description='This is the aliasName: ' + alias_name
    )


def invoke_lambda_with_alias(function_name, alias):
    return lambda_client().invoke(
        FunctionName=function_name,
        Qualifier=alias
    )


if __name__ == '__main__':
    # print(create_access_lambda())
    # print(create_execution_role_lambda())
    # print(attach_access_policy_to_excution_role())
    # print(
    # deploy_lambda_function(PYTHON_LAMBDA_NAME, PYTHON_RUNTIME, LAMBDA_HANDLER, LAMBDA_ROLE_ARN, 'lambda_functions'))
    # env_variables={
    #     'Variables' : {
    #         'ENV_VAR_TEST' : 'This is the environment variable!'
    #     }
    # }
    # add_environment_variables_to_lambda(PYTHON_LAMBDA_NAME, env_variables)
    # print(publish_a_new_version(PYTHON_LAMBDA_NAME))
    # create_alias_for_new_version(PYTHON_LAMBDA_NAME, 'PROD', '1')
    #
    print(update_lambda_function_code(PYTHON_LAMBDA_NAME, 'lambda_functions'))
    response = invoke_lambda_function(PYTHON_LAMBDA_NAME)
    print(response['Payload'].read().decode())
