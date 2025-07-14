import json
import psycopg2
from utils.custom_exceptions import ValidationError, ActiveResourceNotFoundError, ResourceNotFoundError
from utils.logger import logger

def lambda_exception_handler_wrapper(handler_func):

    def wrapped_handler(event, context):
        try:
            return handler_func(event, context)

        except ValidationError as e:
            logger.warning(f'Validation error: {e.message}')
            return {
                'statusCode': e.status_code,
                'body': json.dumps({'error': e.message})
            }

        except ActiveResourceNotFoundError as e:
            logger.warning(f'Active Resource not found: {e.message}')
            return {
                'statusCode': e.status_code,
                'body': json.dumps({'error': e.message})
            }
        
        except ResourceNotFoundError as e:
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

    return wrapped_handler
