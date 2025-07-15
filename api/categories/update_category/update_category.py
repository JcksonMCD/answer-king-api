import json
import psycopg2.extras
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import validate_category_event_body, extract_id_path_param
from utils.json_default import json_default
from utils.custom_exceptions import ActiveResourceNotFoundError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def update_category_in_db(category_id, category):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE categories
                    SET name = %s
                    WHERE id = %s AND deleted = false
                    RETURNING id, name;
                    """,
                    (category.name, category_id)
                )
                row = cursor.fetchone()
                if not row:
                    logger.info(f"Category with ID {category_id} not found.")
                    raise ActiveResourceNotFoundError(f"Category with ID {category_id} not found")

                return row
        
    except psycopg2.Error as e:
        logger.error(f"Database error while updating category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating category: {e}")
        raise

@lambda_exception_handler_wrapper
def lambda_handler(event, context):
    category_id = extract_id_path_param(event)

    updated_category = validate_category_event_body(event)

    update_category_response = update_category_in_db(category_id, updated_category)

    return {
        'statusCode': 200,
        'body': json.dumps(update_category_response, default=json_default)
    }