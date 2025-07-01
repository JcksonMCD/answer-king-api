import os
import json
import psycopg2
from db_connection import get_db_connection

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        name = body['name']
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request data'})
        }

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO categories (name)
                    VALUES (%s)
                    RETURNING id, created_at;
                    """,
                    (name,))
                
                category_id, created_at = cursor.fetchone()
                conn.commit()
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'id': category_id,
                'name': name,
                'created_at': created_at.isoformat()
            })
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }