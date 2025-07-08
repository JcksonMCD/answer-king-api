import json

def extract_id(event, logger):
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