import json
import psycopg2
import logging
from db_connection import get_db_connection
from validate_id_path_param import extract_id
from get_active_row_from_table import get_active_row_from_table
from json_default import json_default

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def validate_category_exists(cursor, category_id):
    if not get_active_row_from_table(cursor, table_name='categories', id=category_id):
        logger.error(f"No Active Category found at ID: {category_id}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error' : f'No Active Category found at ID: {category_id}'
            })
        }
    
    return None

def fetch_items_by_category_from_db(category_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                validation_error = validate_category_exists(cursor, category_id)
                if validation_error:
                    return validation_error

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

                return {
                    'statusCode': 200,
                    'body': json.dumps(items, default=json_default)
                }
            
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
        category_id_response = extract_id(event, logger)
        if isinstance(category_id_response, dict) and 'statusCode' in category_id_response:
            return category_id_response

        category_id = category_id_response

        response = fetch_items_by_category_from_db(category_id)

        return response

    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
