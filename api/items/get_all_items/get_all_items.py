import logging
import json
import psycopg2
import datetime
from db_connection import get_db_connection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def json_default(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)

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
        logger.error(f"Database error while fetching items: {e}")
        raise psycopg2.DatabaseError(f"Failed to retrieve items from database: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching items: {e}")
        raise psycopg2.DatabaseError(f"Unexpected error: {str(e)}")

def lambda_handler(event, context):
    try:
        items = get_all_items_from_db()
        
        logger.info(f"Successfully processed request, returning {len(items)} items")

        return {
            'statusCode': 200,
            'body': json.dumps(items, default=json_default)
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