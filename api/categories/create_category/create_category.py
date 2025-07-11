import json
import psycopg2
from utils.db_connection import get_db_connection
from utils.validation import validate_category_event_body
from utils.json_default import json_default
from utils.custom_exceptions import ValidationError, DatabaseInsertError
from utils.logger import logger

def post_category_to_db(name):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO categories (name)
                    VALUES (%s)
                    RETURNING id, name, created_at;
                    """,
                    (name,))
                
                response = cursor.fetchone()

                if not response:
                    logger.error("Failed to insert category - no result returned")
                    raise DatabaseInsertError("Failed to create category", status_code=500)

                colnames = [desc[0] for desc in cursor.description]
                category = dict(zip(colnames, response))
                conn.commit()
                
                return category
           
    except psycopg2.Error as e:
        logger.error(f"Database error while creating category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating category: {e}")
        raise
    
def lambda_handler(event, context):
    try:
        category_name = validate_category_event_body(event)
        create_category_response = post_category_to_db(category_name)
        
        logger.info(f'Create category successful: {create_category_response}')
        return {
            'statusCode': 201,
            'body': json.dumps(create_category_response, default=json_default)
        }

    except ValidationError as e:
        logger.warning(f'Validation error: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except DatabaseInsertError as e:
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
