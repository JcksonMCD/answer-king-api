import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        table = dynamodb.create_table(
            TableName='answer-king-db',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'type', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 2, 'WriteCapacityUnits': 2},
            GlobalSecondaryIndexes = [
                {
                    'IndexName': 'TypeIndex',
                    'KeySchema': [
                        {'AttributeName': 'type', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
                },
                {
                    'IndexName': 'ReverseLookupIndex',
                    'KeySchema': [
                        {'AttributeName': 'SK', 'KeyType': 'HASH'},
                        {'AttributeName': 'PK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
                }
            ]
        )
        return {"status": "creating", "tableStatus": table.table_status}
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            return {"status": "already_exists"}
        else:
            raise
