import boto3
import json

print('Loading function')
postgres = boto3.client('rds')

def lambda_handler(event, context):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
