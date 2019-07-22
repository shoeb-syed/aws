import os
import json
import boto3

def handler(event, context):
    # TODO implement
    bucket = event['Records'][0]['s3']['bucket']['name']
    sourceKey = event['Records'][0]['s3']['object']['key']
    client = boto3.client('glue')
    client.start_job_run(
        JobName = 'lambda_glue',
        Arguments = {
            "--bucket": bucket,
            "--path": sourceKey
        }
    )