import json
import psycopg2.extras
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.json_default import json_default
from utils.custom_exceptions import DatabaseInsertError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def post_order_to_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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
                
                logger.info(f"Order creation successful")
                return response

    except psycopg2.Error as e:
        logger.error(f"Database error while creating order: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating order: {e}")
        raise

@lambda_exception_handler_wrapper
def lambda_handler(event, context):
    create_order_response = post_order_to_db()
            
    return {
        'statusCode': 200,
        'body': json.dumps(create_order_response, default=json_default)
    }
