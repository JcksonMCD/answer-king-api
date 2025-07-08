import logging
import json
import psycopg2
from db_connection import get_db_connection
from validate_items_request_body import validate_event_body

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        validation_result = validate_event_body(event, logger)

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
                'price': price,
                'description': description,
                'created_at': created_at.isoformat()
            })
        }
    
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }