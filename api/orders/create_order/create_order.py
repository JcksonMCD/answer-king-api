import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.json_default import json_default
from utils.custom_exceptions import DatabaseInsertError

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
                    raise DatabaseInsertError("Failed to create order - no result returned")
                
                colnames = [desc[0] for desc in cursor.description]
                order = dict(zip(colnames, response))
                conn.commit()
                
                logger.info(f"Order creation successful")
                return order
    
    except psycopg2.Error as e:
        logger.error(f"Database error while creating order: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating order: {e}")
        raise
    
def lambda_handler(event, context):
    try:
        create_order_response = post_order_to_db()
                
        return {
            'statusCode': 200,
            'body': json.dumps(create_order_response, default=json_default)
        }
        
    except DatabaseInsertError as e:
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