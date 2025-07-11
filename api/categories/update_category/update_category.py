import json
import psycopg2
import logging
from db_connection import get_db_connection
from validate_categories_request_body import validate_event_body
from json_default import json_default
from validate_id_path_param import extract_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'No active Category not found at ID: {category_id}'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                category = dict(zip(colnames, row))

                return category
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
    except Exception as e:
        logger.error(f"Unexpected error while updating item: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def lambda_handler(event, context):
    try:
        category_id_response = extract_id(event, logger)
        if isinstance(category_id_response, dict) and 'statusCode' in category_id_response:
            return category_id_response

        category_id = category_id_response

        validation_result = validate_event_body(event, logger)
        if isinstance(validation_result, dict) and 'statusCode' in validation_result:
            return validation_result
        
        name = validation_result

        update_category_response = update_category_in_db(category_id, name)
        if isinstance(update_category_response, dict) and 'statusCode' in update_category_response:
            return update_category_response

        return {
            'statusCode': 200,
            'body': json.dumps(update_category_response, default=json_default)
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }