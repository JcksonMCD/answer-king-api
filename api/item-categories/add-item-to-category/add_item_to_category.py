import os
import json
import psycopg2

def lambda_handler(event, context):
    try:
        category_id = int(event['pathParameters']['id'])
        item_id = int(event["queryStringParameters"]['itemID'])

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Category and Item ID\'s must be provided'})
        }

    try:
        with psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        ) as conn:
            with conn.cursor() as cursor:
                
                cursor.execute(
                    """
                    INSERT INTO item_categories (item_id, category_id)
                    VALUES (%s, %s)
                    """,
                    (item_id, category_id))
                        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message' : f'Successfully added Item at ID {item_id} to Category at ID {category_id}'
            })
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
