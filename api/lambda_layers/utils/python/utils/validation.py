import json
import pydantic
from .logger import logger
from .custom_exceptions import ValidationError, ActiveResourceNotFoundError
from .models import Category

def validate_category_event_body(event):
    if not event.get('body'):
        raise ValidationError('Request body is required')

    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        raise ValidationError('Invalid JSON format')

    try:
        category = Category.model_validate(body)
    except pydantic.ValidationError as e:
        raise ValidationError(e.errors()[0]['msg'])

    return category

def validate_item_event_body(event):
    if not event.get('body'):
        raise ValidationError('Request body is required')

    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in request body: {e}")
        raise ValidationError('Invalid JSON format')

    name = body.get('name')
    if not name or not isinstance(name, str):
        raise ValidationError('Name field is required and must be of type string')

    name = name.strip()
    if not name:
        raise ValidationError('Name field must not be empty')

    price_raw = body.get('price')
    if price_raw is None:
        raise ValidationError('Price is required')

    try:
        price = float(price_raw)
        if price != round(price, 2):
            raise ValidationError('Price has to be to two decimal points')
        if price < 0:
            raise ValidationError('Price cannot be negative')
    except (ValueError, TypeError):
        raise ValidationError('Price must be a valid number')

    description = body.get('description')

    return name, price, description

def extract_item_id_from_query_param(event):
    query_params = event.get('queryStringParameters') or {}
    item_id = query_params.get('itemID')

    if not item_id:
        logger.info('No query string parameter labeled itemID')
        raise ValidationError('Invalid or missing ID in path. Must use query string parameter labeled itemID')

    try:
        return int(item_id)
    except ValueError as e:
        logger.error(f'Query string parameter ID not an int value: {e}')
        raise ValidationError('ID must be an integer')
    
def extract_id_path_param(event):
    path_params = event.get('pathParameters') or {}
    item_id = path_params.get('id')

    if not item_id:
        logger.info('No path parameter labeled id')
        raise ValidationError('Invalid or missing path ID')

    try:
        return int(item_id)
    except ValueError as e:
        logger.error(f'Path ID not an int value: {e}')
        raise ValidationError('ID must be an integer')

def get_active_row_from_table(cursor, table_name, id):
    allowed_tables = {'items', 'categories', 'item_categories', 'orders'}
    
    if table_name.lower() not in (table.lower() for table in allowed_tables):
        raise ValidationError(f"Invalid table name: {table_name}")

    query = f"SELECT id FROM {table_name} WHERE id = %s AND deleted = false;"
    cursor.execute(query, (id,))
    
    response = cursor.fetchone()
    if not response:
        logger.error(f'No Active {table_name} found at ID: {id}')
        raise ActiveResourceNotFoundError(f'No Active {table_name} found at ID: {id}')
    
    return response