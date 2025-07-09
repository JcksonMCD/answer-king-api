import json
import psycopg2
import logging
from db_connection import get_db_connection
from validate_id_path_param import extract_id
from validate_item_id_query_param import extract_item_id
from get_active_row_from_table import get_active_row_from_table

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_and_validate_ids(event):
    category_id_response = extract_id(event, logger)
    if isinstance(category_id_response, dict) and 'statusCode' in category_id_response:
        return category_id_response

    category_id = category_id_response
    
    item_id_response = extract_item_id(event, logger)
    if isinstance(item_id_response, dict) and 'statusCode' in item_id_response:
        return item_id_response
    
    item_id = item_id_response

    return category_id, item_id

def validate_entities_exist(cursor, category_id, item_id):
    if not get_active_row_from_table(cursor, table_name='items', id=item_id):
        logger.error(f'No Active Item found at ID: {item_id}')
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error' : f'No Active Item found at ID: {item_id}'
            })
        }
                
    if not get_active_row_from_table(cursor, table_name='categories', id=category_id):
        logger.error(f"No Active Category found at ID: {category_id}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                 'error' : f'No Active Category found at ID: {category_id}'
            })
        }
    
    return None

def create_item_category_association(cursor, category_id, item_id):
    try:
        cursor.execute(
        """
        INSERT INTO item_categories (item_id, category_id)
        VALUES (%s, %s)
        """,
        (item_id, category_id))
            
        return None
    
    except psycopg2.errors.UniqueViolation:
        logger.error(f"Item at ID {item_id} is already added to Category with ID {category_id}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error' : f'Item at ID {item_id} is already added to Category with ID {category_id}'
            })
        }  

def post_item_to_category_in_db(category_id, item_id):
    try:        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:

                validation_error = validate_entities_exist(cursor, category_id, item_id)
                if validation_error:
                    return validation_error
                
                association_error = create_item_category_association(cursor, category_id, item_id)
                if association_error:
                    return association_error
                
                conn.commit()
                
                logger.info(f'Successfully added Item at ID {item_id} to Category at ID {category_id}')   

                return {
                    'statusCode': 201,
                    'body': json.dumps({
                        'message' : f'Successfully added Item at ID {item_id} to Category at ID {category_id}'
                    })
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
            'body': json.dumps({'error': f'Internal server error'})
        }

def lambda_handler(event, context):
    try:
        ids_response = extract_and_validate_ids(event)
        if isinstance(ids_response, dict):
             return ids_response
        
        category_id, item_id = ids_response

        response = post_item_to_category_in_db(category_id, item_id)
                        
        return response
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error'})
        }

