import logging
import json
import psycopg2
from db_connection import get_db_connection
from validate_items_request_body import validate_event_body
from json_default import json_default
from validate_id_path_param import extract_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        item_id_response = extract_id(event, logger)
        if isinstance(item_id_response, dict) and 'statusCode' in item_id_response:
            return item_id_response

        item_id = item_id_response

        validation_result = validate_event_body(event, logger)
        if isinstance(validation_result, dict) and 'statusCode' in validation_result:
            return validation_result
        
        name, price, description = validation_result

        update_item_response = update_item_in_db(item_id, name, price, description)
        if isinstance(update_item_response, dict) and 'statusCode' in update_item_response:
            return update_item_response

        return {
            'statusCode': 200,
            'body': json.dumps(update_item_response, default=json_default)
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error'})
        }