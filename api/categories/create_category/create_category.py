import json
import psycopg2.extras
from utils.db_connection import get_db_connection
from utils.validation import validate_category_event_body
from utils.json_default import json_default
from utils.custom_exceptions import DatabaseInsertError
from utils.logger import logger
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def post_category_to_db(category):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO categories (name)
                    VALUES (%s)
                    RETURNING id, name, created_at;
                    """,
                    (category.name,))
                
                response = cursor.fetchone()

                if not response:
                    logger.error("Failed to insert category - no result returned")
                    raise DatabaseInsertError("Failed to create category", status_code=500)
                
                return response
           
    except psycopg2.Error as e:
        logger.error(f"Database error while creating category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating category: {e}")
        raise

@lambda_exception_handler_wrapper    
def lambda_handler(event, context):
    category = validate_category_event_body(event)
    category_data = post_category_to_db(category)
    
    logger.info(f'Create category successful: {category_data}')
    return {
        'statusCode': 201,
        'body': json.dumps(category_data, default=json_default)
    }