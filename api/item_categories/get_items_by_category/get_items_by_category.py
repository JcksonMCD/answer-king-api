import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import extract_id_path_param, get_active_row_from_table
from utils.json_default import json_default
from utils.custom_exceptions import ValidationError, ActiveResourceNotFoundError

def fetch_items_by_category_from_db(category_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                get_active_row_from_table(cursor, table_name='categories', id=category_id)

                cursor.execute(
                    """
                    SELECT items.id, items.name, items.price 
                    FROM item_categories
                    INNER JOIN items ON item_categories.item_id = items.id
                    WHERE item_categories.category_id = %s AND items.deleted = FALSE
                    ORDER BY items.name;
                    """,
                    (category_id,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                items = [dict(zip(columns, row)) for row in rows]

                logger.info(f"Successfully fetched {len(items)} items for category {category_id}")
                return items
            
    except psycopg2.Error as e:
        logger.error(f"Database error while fetching all items in a category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching all items in a category: {e}")
        raise
    
def lambda_handler(event, context):
    try:
        category_id = extract_id_path_param(event)

        items = fetch_items_by_category_from_db(category_id)

        return {
            'statusCode': 200,
            'body': json.dumps(items, default=json_default)
        }
    
    except ValidationError as e:
        logger.warning(f'Validation error: {e.message}')
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error': e.message})
        }
    except ActiveResourceNotFoundError as e:
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

