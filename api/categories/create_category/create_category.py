import logging
import json
import psycopg2
from db_connection import get_db_connection
from validate_categories_request_body import validate_event_body
from json_default import json_default

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Failed to create category'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                category = dict(zip(colnames, response))
                conn.commit()
                
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
        validation_result = validate_event_body(event, logger)
        if isinstance(validation_result, dict) and 'statusCode' in validation_result:
            return validation_result
        
        category_name = validation_result

        create_category_response = post_category_to_db(category_name)
        if isinstance(create_category_response, dict) and 'statusCode' in create_category_response:
            return create_category_response
        
        logger.info(f'Create category successfull: {create_category_response}')
        return {
            'statusCode': 201,
            'body': json.dumps(create_category_response, default=json_default)
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }