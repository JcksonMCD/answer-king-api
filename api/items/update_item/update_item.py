import os
import json
import psycopg2
import decimal
from db_connection import get_db_connection

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return str(obj)  

def lambda_handler(event, context):
    try:
        item_id = int(event['pathParameters']['id'])
        body = json.loads(event['body'])
        name = body['name']
        if not name:
            assert TypeError
        price = float(body['price'])
        description = body.get('description')
    except (KeyError, TypeError, ValueError):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid or missing ID in path or request data'})
        }
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE items
                    SET name = %s, price = %s, description = %s
                    WHERE id = %s AND deleted = FALSE
                    RETURNING id, name, price, description;
                    """,
                    (name, price, description, item_id)
                )
                row = cursor.fetchone()
                if not row:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'No Active Item found at ID: {item_id}'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                item = dict(zip(colnames, row))

        return {
            'statusCode': 200,
            'body': json.dumps(item, default=decimal_default)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }