import json
import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import extract_id_path_param, extract_item_id_from_query_param, get_active_row_from_table
from utils.custom_exceptions import ValidationError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def extract_and_validate_ids(event):
    category_id = extract_id_path_param(event, logger)
    item_id = extract_item_id_from_query_param(event, logger)

    return category_id, item_id
    
def validate_entities_exist(cursor, category_id, item_id):
    get_active_row_from_table(cursor, table_name='items', id=item_id)
    get_active_row_from_table(cursor, table_name='categories', id=category_id)

def create_item_category_association(cursor, category_id, item_id):
    try:
        cursor.execute(
        """
        INSERT INTO item_categories (item_id, category_id)
        VALUES (%s, %s)
        """,
        (item_id, category_id))
            
    except psycopg2.errors.UniqueViolation as e:
        message = f"Item at ID {item_id} is already added to Category with ID {category_id}"
        logger.error(message)
        raise ValidationError(message)

def post_item_to_category_in_db(category_id, item_id):
    try:        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                validate_entities_exist(cursor, category_id, item_id)
                
                create_item_category_association(cursor, category_id, item_id)
                                
                message = f'Successfully added Item at ID {item_id} to Category at ID {category_id}'
                logger.info(message)   
                return {
                    'statusCode': 201,
                    'body': json.dumps({
                        'message' : message
                    })
                }
               
    except psycopg2.Error as e:
        logger.error(f"Database error while adding item to category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while adding item to category: {e}")
        raise

@lambda_exception_handler_wrapper
def lambda_handler(event, context):
    category_id, item_id = extract_and_validate_ids(event)

    return post_item_to_category_in_db(category_id, item_id)