import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import validate_item_event_body, extract_id_path_param
from utils.json_default import json_default
from utils.custom_exceptions import ActiveResourceNotFoundError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def update_item_in_db(item_id, item):
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
                    (item.name, item.price, item.description, item_id)
                )
                row = cursor.fetchone()

                if not row:
                    logger.info(f"Active Item with ID {item_id} not found.")
                    raise ActiveResourceNotFoundError(f"Active Item with ID {item_id} not found")
                
                colnames = [desc[0] for desc in cursor.description]
                item = dict(zip(colnames, row))
                conn.commit()
            
                logger.info(f'Successfully update item with ID: {item_id}')
                return item
                
    except psycopg2.Error as e:
        logger.error(f"Database error while updating item: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating item: {e}")
        raise

@lambda_exception_handler_wrapper  
def lambda_handler(event, context):
    item_id = extract_id_path_param(event)
    item = validate_item_event_body(event)
    
    update_item_response = update_item_in_db(item_id, item)

    return {
        'statusCode': 200,
        'body': json.dumps(update_item_response, default=json_default)
    }
