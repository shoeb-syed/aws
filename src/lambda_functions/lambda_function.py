import os
import json
import boto3

def handler(event, context):
    # TODO implement
    sourceKey = event['Records'][0]['s3']['object']['key']
    client = boto3.client('glue')
    client.start_job_run(
        JobName = 'lambda_glue',
        Arguments = {
            "--path": sourceKey
        }
    )
    print(sourceKey)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }