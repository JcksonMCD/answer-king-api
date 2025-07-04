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
    except (KeyError, TypeError, ValueError):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid or missing ID in path'})
        }
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, price, description, created_at 
                    FROM items
                    WHERE id = %s AND deleted = FALSE;
                    """,
                    (item_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'No active Item found at ID: {item_id}'})
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