import json

def extract_item_id(event, logger):
    try:
        query_params = event.get('queryStringParameters') or {}
        item_id = query_params.get('itemID')

        if not item_id:
            logger.info('No query string parameter labeled itemID')
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid or missing ID in path. Must use query string parameter labeled itemID'})
            }
        
        return int(item_id)
    except ValueError as e:
        logger.error(f'Query string parameter ID not an int value: {e}')
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'ID must be an integer'})
        }