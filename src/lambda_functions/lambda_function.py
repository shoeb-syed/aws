import boto3
import os

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    sourceKey = event['Records'][0]['s3']['object']['key']
    glueJobName = os.environ['GlueJobName']
    client = boto3.client('glue')
    client.start_job_run(
        JobName=glueJobName,
        Arguments={
            "--bucket": bucket,
            "--path": sourceKey
        }
    )