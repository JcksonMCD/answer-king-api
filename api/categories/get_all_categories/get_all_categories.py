import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.json_default import json_default
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def get_all_categories_from_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, created_at FROM categories
                    WHERE deleted = false
                    ORDER BY created_at DESC;
                    """
                    )
                rows = cursor.fetchall()

                if not rows:
                    logger.info('No categories found in databse')
                    return []
                
                columns = [desc[0] for desc in cursor.description]
                categories = [dict(zip(columns, row)) for row in rows]

                logger.info(f"Successfully retrieved {len(categories)} categories")
                
                return categories
                
    except psycopg2.Error as e:
        logger.error(f"Database error while fetching all categories: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching all categories: {e}")
        raise

@lambda_exception_handler_wrapper
def lambda_handler(event, context):
    categories = get_all_categories_from_db()
    
    logger.info(f"Successfully processed request, returning {len(categories)} categories")

    return {
        'statusCode': 200,
        'body': json.dumps(categories, default=json_default)
    }
