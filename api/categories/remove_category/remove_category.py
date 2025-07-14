import psycopg2
from utils.logger import logger
from utils.db_connection import get_db_connection
from utils.validation import extract_id_path_param
from utils.custom_exceptions import ResourceNotFoundError
from utils.lambda_exception_handler_wrapper import lambda_exception_handler_wrapper

def delete_category_from_db(category_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE categories 
                    SET deleted = true
                    WHERE id = %s
                    RETURNING id;

                    """,
                    (category_id,)
                )

                deleted = cursor.fetchone()
                if not deleted:
                    logger.info(f"Category with ID {category_id} not found for deletion.")
                    raise ResourceNotFoundError(f"Category with ID {category_id} not found")

                conn.commit()
                
                deleted_id = deleted[0]
                return deleted_id
            
    except psycopg2.Error as e:
        logger.error(f"Database error while deleting category: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting category: {e}")
        raise

@lambda_exception_handler_wrapper
def lambda_handler(event, context):
    category_id = extract_id_path_param(event)
    
    deleted = delete_category_from_db(category_id)

    logger.info(f'Category successfully deleted at ID: {deleted}')
    return {
        'statusCode': 204,
        'body': ''
    }
