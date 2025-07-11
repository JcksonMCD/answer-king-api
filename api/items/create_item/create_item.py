import logging
import json
import psycopg2
from db_connection import get_db_connection
from validate_items_request_body import validate_event_body
from json_default import json_default

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
                
                response = cursor.fetchone()

                if not response:
                    logger.error("Failed to insert item - no result returned")
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Failed to create item'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                item = dict(zip(colnames, response))
                conn.commit()

        return item
                
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

        post_item_response = post_item_to_db(name, price, description)
        if isinstance(post_item_response, dict) and 'statusCode' in post_item_response:
            return post_item_response

        logger.info(f"Successfully created item: {post_item_response}")
        return {
            'statusCode': 201,
            'body': json.dumps(post_item_response, default=json_default)
        }
    
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }