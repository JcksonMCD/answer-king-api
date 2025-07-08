import json
import psycopg2
import logging
from db_connection import get_db_connection
from validate_id_path_param import extract_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def delete_category_from_db(category_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE categories 
                    SET deleted = true
                    WHERE id = %s
                    RETURNING id;

                    """,
                    (category_id,)
                )

                deleted = cursor.fetchone()
                if not deleted:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f"No Category found at ID: {category_id}"})
                    }
                
                return deleted
            
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
            'body': json.dumps({'error': f'Internal server error {e}'})
        }

def lambda_handler(event, context):
    try:
        category_id_response = extract_id(event, logger)
        if isinstance(category_id_response, dict) and 'statusCode' in category_id_response:
            return category_id_response
        
        category_id = category_id_response

        deleted_response = delete_category_from_db(category_id)
        if isinstance(deleted_response, dict) and 'statusCode' in deleted_response:
            return deleted_response

        return {
            'statusCode': 204,
            'body': json.dumps({'deleted_category_id': deleted_response[0]})
        }

    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error {e}'})
        }