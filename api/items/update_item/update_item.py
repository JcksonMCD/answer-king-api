import logging
import json
import psycopg2
from db_connection import get_db_connection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_item_id(event):
    try:
        path_params = event.get('pathParameters') or {}
        item_id = path_params.get('id')

        if not item_id:
            logger.info('No path parameter labeled id')
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid or missing ID in path'})
            }
        
        return int(item_id)
    except ValueError as e:
        logger.error(f'Path ID not an int value: {e}')
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'ID must be an integer'})
        }

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
        price = float(price_raw)
        if price != round(price, 2):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Price has to be to two decimal points'})
            }

        if price < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Price cannot be negative'})
            }
        
    except (ValueError, TypeError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Price must be a valid number'})
        }
    
    description = body.get('description')

    return name, price, description

def update_item_in_db(item_id, name, price, description):
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
                conn.commit()
                
        return item
                
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
    except Exception as e:
        logger.error(f"Unexpected error while updating item: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
    
def lambda_handler(event, context):
    try:
        item_id_response = extract_item_id(event)
        if isinstance(item_id_response, dict) and 'statusCode' in item_id_response:
            return item_id_response

        item_id = item_id_response

        body_validation_result = validate_event_body(event)
        if isinstance(body_validation_result, dict) and 'statusCode' in body_validation_result:
            return body_validation_result

        name, price, description = body_validation_result

        update_item_response = update_item_in_db(item_id, name, price, description)
        if isinstance(update_item_response, dict) and 'statusCode' in update_item_response:
            return update_item_response

        return {
            'statusCode': 200,
            'body': json.dumps(update_item_response)
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }