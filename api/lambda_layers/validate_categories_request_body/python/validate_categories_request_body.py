import json

def validate_event_body(event, logger):
    if not event.get('body'):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Request body is required'})
        }
    
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in request body: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    
    name = body.get('name')
    if not name or not isinstance(name, str): 
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Name field is required and must be of type string'})
        }
    
    name = name.strip()
    if not name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Name field must not be empty'})
        }

    return name