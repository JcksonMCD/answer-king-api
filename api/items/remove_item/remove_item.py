import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import extract_id_path_param
from utils.custom_exceptions import ValidationError, ResourceNotFoundError

def remove_item_from_db(item_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE items
                    SET deleted = TRUE
                    WHERE id = %s
                    RETURNING id;
                    """,
                    (item_id,)
                )

                deleted = cursor.fetchone()
                if not deleted:
                    logger.info(f"Item with ID {item_id} not found.")
                    raise ResourceNotFoundError(f"Item with ID {item_id} not found")
                
                conn.commit()
                
                logger.info(f'Successfully processed DELETE request for item ID: {item_id}')

    except psycopg2.Error as e:
        logger.error(f"Database error while deleting item: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting item: {e}")
        raise
    
def lambda_handler(event, context):
    try:
        item_id = extract_id_path_param(event)

        remove_item_from_db(item_id)

        return {
            'statusCode': 204,
            'body': ''
        }

    except ValidationError as e:
        logger.warning(f'Validation error: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except ResourceNotFoundError as e:
        logger.warning(f'Resource not found: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except psycopg2.Error as e:
        logger.error(f'Database error: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
    except Exception as e:
        logger.error(f'Unhandled exception: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }   