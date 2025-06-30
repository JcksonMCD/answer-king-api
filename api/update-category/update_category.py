import os
import json
import psycopg2
import datetime

def json_default(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)  

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
    
    if not name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Empty Name field not accepted'})
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
                        'body': json.dumps({'error': f'No active Category found at ID: {category_id}'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                category = dict(zip(colnames, row))

        return {
            'statusCode': 200,
            'body': json.dumps(category, default=json_default)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }