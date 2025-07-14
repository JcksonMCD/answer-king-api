import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import validate_item_event_body
from utils.json_default import json_default
from utils.custom_exceptions import DatabaseInsertError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def post_item_to_db(name, price, description):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO items (name, price, description)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, price, description, created_at
                    """,
                    (name, price, description))
                
                response = cursor.fetchone()

                if not response:
                    logger.error("Failed to insert item - no result returned")
                    raise DatabaseInsertError("Failed to insert item - no result returned")
                
                colnames = [desc[0] for desc in cursor.description]
                item = dict(zip(colnames, response))
                conn.commit()

                logger.info(f"Successfully created item: {name}")
                return item
                
    except psycopg2.Error as e:
        logger.error(f"Database error while creating item: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating item: {e}")
        raise

@lambda_exception_handler_wrapper   
def lambda_handler(event, context):
    name, price, description = validate_item_event_body(event)

    logger.info(f"Successfully created item: {name}")
    return {
        'statusCode': 201,
        'body': json.dumps(post_item_to_db(name, price, description), default=json_default)
    } 