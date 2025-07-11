import json
import logging
import psycopg2
from db_connection import get_db_connection
from json_default import json_default

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        logger.error(f"Database error while fetching categories: {e}")
        raise psycopg2.DatabaseError(f"Failed to retrieve categories from database: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching categories: {e}")
        raise psycopg2.DatabaseError(f"Unexpected error: {str(e)}")

def lambda_handler(event, context):
    try:
        categories = get_all_categories_from_db()
        
        logger.info(f"Successfully processed request, returning {len(categories)} categories")

        return {
            'statusCode': 200,
            'body': json.dumps(categories, default=json_default)
        }
        
    except psycopg2.DatabaseError as e:
        logger.error(f"Database error in lambda handler: {e}")
        return {
            'statusCode': 500,
            'body': {'error': 'Database error occured'}
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': {'error': 'Internal server'}
        }