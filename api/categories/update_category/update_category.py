import json
import psycopg2
from db_connection import get_db_connection

def lambda_handler(event, context):
    try:
        category_id = int(event['pathParameters']['id'])
        body = json.loads(event['body'])
        name = body['name']
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
                    UPDATE categories
                    SET name = %s
                    WHERE id = %s AND deleted = false
                    RETURNING id, name;
                    """,
                    (name, category_id)
                )
                row = cursor.fetchone()
                if not row:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'No active Category not found at ID: {category_id}'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                category = dict(zip(colnames, row))

        return {
            'statusCode': 200,
            'body': json.dumps(category)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }