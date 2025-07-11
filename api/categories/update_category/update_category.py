import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import validate_category_event_body, extract_id_path_param
from utils.json_default import json_default
from utils.custom_exceptions import ValidationError, ActiveResourceNotFoundError 

def update_category_in_db(category_id, name):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE categories
                    SET name = %s
                    WHERE id = %s AND deleted = false
                    RETURNING id, name;
                    """,
                    (name, category_id)
                )
                row = cursor.fetchone()
                if not row:
                    logger.info(f"Category with ID {category_id} not found.")
                    raise ActiveResourceNotFoundError(f"Category with ID {category_id} not found")
                
                colnames = [desc[0] for desc in cursor.description]
                category = dict(zip(colnames, row))

                return category
        
    except psycopg2.Error as e:
        logger.error(f"Database error while updating category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating category: {e}")
        raise

def lambda_handler(event, context):
    try:
        category_id = extract_id_path_param(event)

        new_category_name = validate_category_event_body(event)

        update_category_response = update_category_in_db(category_id, new_category_name)

        return {
            'statusCode': 200,
            'body': json.dumps(update_category_response, default=json_default)
        }
        
    except ValidationError as e:
        logger.warning(f'Validation error: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except ActiveResourceNotFoundError as e:
        logger.warning(f'Database insert error: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except psycopg2.Error as e:
        logger.error(f'Database error: {e}')
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