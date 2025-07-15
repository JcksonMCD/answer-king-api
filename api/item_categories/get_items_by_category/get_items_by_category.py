import json
import psycopg2.extras
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import extract_id_path_param, get_active_row_from_table
from utils.json_default import json_default
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def fetch_items_by_category_from_db(category_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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

                logger.info(f"Successfully fetched {len(rows)} items for category {category_id}")
                return rows
            
    except psycopg2.Error as e:
        logger.error(f"Database error while fetching all items in a category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching all items in a category: {e}")
        raise

@lambda_exception_handler_wrapper  
def lambda_handler(event, context):
    category_id = extract_id_path_param(event)

    items = fetch_items_by_category_from_db(category_id)

    return {
        'statusCode': 200,
        'body': json.dumps(items, default=json_default)
    }
