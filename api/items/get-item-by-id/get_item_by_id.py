import os
import json
import psycopg2
import decimal

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
                    SELECT * FROM items
                    WHERE id = %s;
                    """,
                    (item_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'Item not found at ID: {item_id}'})
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