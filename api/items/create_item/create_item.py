import os
import json
import psycopg2
from db_connection import get_db_connection

def lambda_handler(event, context):
    # Parse and validate request
    try:
        body = json.loads(event['body'])
        name = body.get('name')
        if not name: 
            raise KeyError('Name field missing')
        price = float(body['price'])  # Validate numeric type
        description = body.get('description')
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request data'})
        }

    # Database operation
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO items (name, price, description)
                    VALUES (%s, %s, %s)
                    RETURNING id, created_at
                    """,
                    (name, price, description))
                
                item_id, created_at = cursor.fetchone()
        
        # Format response
        return {
            'statusCode': 201,
            'body': json.dumps({
                'id': item_id,
                'name': name,
                'price': price,
                'description': description,
                'created_at': created_at.isoformat()
            })
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }