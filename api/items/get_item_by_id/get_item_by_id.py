import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.json_default import json_default
from utils.validation import extract_id_path_param
from utils.custom_exceptions import ValidationError, ActiveResourceNotFoundError

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
    
def lambda_handler(event, context):
    try:
        item_id = extract_id_path_param(event)

        return {
            'statusCode': 200,
            'body': json.dumps(get_item_from_db(item_id), default=json_default)
        }
        
    except ValidationError as e:
        logger.warning(f'Validation error: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except ActiveResourceNotFoundError as e:
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