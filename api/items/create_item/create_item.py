import json
import psycopg2
from db_connection import get_db_connection

def load_event_body(event):
    if not event.get('body'):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Request body is required'})
        }
    
    try:
        body = json.loads(event['body'])

        name = body.get('name')
        if not name or not isinstance(name, str): 
            raise ValueError('Name field requires a value')
        
        price = float(body['price'])
        description = body.get('description')
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request data'})
        }
    
    return name, price, description

def post_item_to_db(name, price, description):
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
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
    
    return item_id, created_at

def lambda_handler(event, context):
    name, price, description = load_event_body(event)

    item_id, created_at = post_item_to_db(name, price, description)

    return {
        'statusCode': 201,
        'body': json.dumps({
            'id': item_id,
            'name': name,
            'price': price,
            'description': description,
            'created_at': str(created_at)
        })
    }
        
