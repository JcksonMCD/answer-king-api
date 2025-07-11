import json
import psycopg2
import logging
from db_connection import get_db_connection
from json_default import json_default

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def post_order_to_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO orders
                    DEFAULT VALUES
                    RETURNING id, status, total, 
                    created_at;
                    """,
                    )
                
                response = cursor.fetchone()
                if not response:
                    logger.error("Failed to create order - no result returned")
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Failed to create order'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                order = dict(zip(colnames, response))
                conn.commit()
        
        return order
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
        create_order_response = post_order_to_db()
        if isinstance(create_order_response, dict) and 'statusCode' in create_order_response:
            return create_order_response
                
        logger.info(f"Order creation successful: {create_order_response}")
        return {
            'statusCode': 200,
            'body': json.dumps(create_order_response, default=json_default)
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }