import json
import boto3
from src.common.models.order import Order

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('answer-king-db')

def lambda_handler(event, context):
    order = Order()

    table.putItem(order.to_dynamodb_item())

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Order saved", "order_pk": order.order_pk}),
    }
