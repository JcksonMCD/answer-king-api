import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.json_default import json_default
from utils.validation import extract_id_path_param
from utils.custom_exceptions import ActiveResourceNotFoundError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def get_item_from_db(item_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, price, description, created_at 
                    FROM items
                    WHERE id = %s AND deleted = FALSE;
                    """,
                    (item_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.info(f"Active Item with ID {item_id} not found.")
                    raise ActiveResourceNotFoundError(f"Active Item with ID {item_id} not found")
                
                colnames = [desc[0] for desc in cursor.description]
                item = dict(zip(colnames, row))

                logger.info(f'Successfully retrieved item with ID: {item_id}')
                return item
    
    except psycopg2.Error as e:
        logger.error(f"Database error while fetching item: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching item: {e}")
        raise

@lambda_exception_handler_wrapper  
def lambda_handler(event, context):
    item_id = extract_id_path_param(event)

    return {
        'statusCode': 200,
        'body': json.dumps(get_item_from_db(item_id), default=json_default)
    }
