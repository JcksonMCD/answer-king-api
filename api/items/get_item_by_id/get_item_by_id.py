import logging
import json
import psycopg2
from db_connection import get_db_connection
from json_default import json_default

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_item_id(event):
    try:
        path_params = event.get('pathParameters') or {}
        item_id = path_params.get('id')

        if not item_id:
            logger.info('No path parameter labeled id')
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid or missing ID in path'})
            }
        
        return int(item_id)
    except ValueError as e:
        logger.error(f'Path ID not an int value: {e}')
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'ID must be an integer'})
        }
    
def get_item_from_db(item_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, price, description, created_at 
                    FROM items
                    WHERE id = %s AND deleted = FALSE;
                    """,
                    (item_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.error(f'No item found at ID: {item_id}')
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'No active Item found at ID: {item_id}'})
                    }
                
                colnames = [desc[0] for desc in cursor.description]
                item = dict(zip(colnames, row))

                logger.info(f'Successfully retrieved item with ID: {item_id}')
                return item
    except psycopg2.Error as e:
        logger.error(f'Error occured while fetching item from database: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }
    except Exception as e:
        logger.error(f'Unexpected error while fetching item {item_id}: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
    
def lambda_handler(event, context):
    try:
        item_id_result = extract_item_id(event)

        if isinstance(item_id_result, dict) and 'statusCode' in item_id_result:
            return item_id_result
        
        item_id = item_id_result

        db_result = get_item_from_db(item_id)
        if isinstance(db_result, dict) and 'statusCode' in db_result:
            return db_result
                
        logger.info(f'Successfully processed request for item ID: {item_id}')
        return {
            'statusCode': 200,
            'body': json.dumps(db_result, default=json_default)
        }
        
    except Exception as e:
        logger.error(f'Unhandled exception in lambda_handler: {e}', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Exception occured'})
        }