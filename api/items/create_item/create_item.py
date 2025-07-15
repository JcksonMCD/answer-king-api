import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import validate_item_event_body
from utils.json_default import json_default
from utils.custom_exceptions import DatabaseInsertError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def post_item_to_db(item):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO items (name, price, description)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, price, description, created_at
                    """,
                    (item.name, item.price, item.description))
                
                response = cursor.fetchone()

                if not response:
                    logger.error("Failed to insert item - no result returned")
                    raise DatabaseInsertError("Failed to insert item - no result returned")
                
                colnames = [desc[0] for desc in cursor.description]
                item_dict = dict(zip(colnames, response))

                logger.info(f"Successfully created item: {item.name}")
                return item_dict
                
    except psycopg2.Error as e:
        logger.error(f"Database error while creating item: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating item: {e}")
        raise

@lambda_exception_handler_wrapper   
def lambda_handler(event, context):
    item = validate_item_event_body(event)
    created_item = post_item_to_db(item)

    logger.info(f"Successfully created item: {item.name}")
    return {
        'statusCode': 201,
        'body': json.dumps(created_item, default=json_default)
    } 