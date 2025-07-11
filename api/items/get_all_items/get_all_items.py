import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.json_default import json_default

def get_all_items_from_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               SELECT id, name, price, description, created_at 
                               FROM items 
                               WHERE deleted = FALSE 
                               ORDER BY created_at DESC;

                               """)
                rows = cursor.fetchall()

                if not rows:
                    logger.info('No items found in databse')
                    return []
                
                columns = [desc[0] for desc in cursor.description]
                items = [dict(zip(columns, row)) for row in rows]

                logger.info(f"Successfully retrieved {len(items)} items")
                return items
                
    except psycopg2.Error as e:
        logger.error(f"Database error while fetching all items: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching all: {e}")
        raise

def lambda_handler(event, context):
    try:
        items = get_all_items_from_db()

        logger.info(f"Successfully processed request, returning {len(items)} items")
        return {
            'statusCode': 200,
            'body': json.dumps(items, default=json_default)
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