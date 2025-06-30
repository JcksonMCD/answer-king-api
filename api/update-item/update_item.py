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
        body = json.loads(event['body'])
        name = body['name']
        price = float(body['price'])
        description = body.get('description')
    except (KeyError, TypeError, ValueError):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid or missing id in path or request data'})
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
                    UPDATE items
                    SET name = %s, price = %s, description = %s
                    WHERE id = %s
                    RETURNING *;
                    """,
                    (name, price, description, item_id)
                )
                row = cursor.fetchone()
                if not row:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Item not found'})
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