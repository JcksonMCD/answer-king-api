from decimal import Decimal
import decimal
import logging
import json
import psycopg2
from db_connection import get_db_connection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def validate_event_body(event):
    if not event.get('body'):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Request body is required'})
        }
    
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in request body: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    
    name = body.get('name')
    if not name or not isinstance(name, str): 
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Name field is required and must be of type string'})
        }
    
    name = name.strip()
    if not name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Name field must not be empty'})
        }
    
    price_raw = body.get('price')
    if price_raw is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Price is required'})
        }
    
    try:
        price = Decimal(str(price_raw))

        if price < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Price cannot be negative'})
            }
        
    except (decimal.InvalidOperation, ValueError, TypeError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Price must be a valid number'})
        }
    
    description = body.get('description')

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
                
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    logger.error("Failed to insert item - no result returned")
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Failed to create item'})
                    }
                
        return result
                
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
    
def lambda_handler(event, context):
    try:
        validation_result = validate_event_body(event)

        if isinstance(validation_result, dict) and 'statusCode' in validation_result:
            return validation_result
        
        name, price, description = validation_result

        db_result = post_item_to_db(name, price, description)
        if isinstance(db_result, dict) and 'statusCode' in db_result:
            return db_result

        item_id, created_at = db_result
        logger.info(f"Successfully created item with ID: {item_id}")

        return {
            'statusCode': 201,
            'body': json.dumps({
                'id': item_id,
                'name': name,
                'price': str(price),
                'description': description,
                'created_at': str(created_at)
            })
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }