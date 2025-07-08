import json
import psycopg2
from db_connection import get_db_connection

def get_active_item(cursor, item_id):
    cursor.execute(
        "SELECT id FROM items WHERE id = %s AND deleted = false;", (item_id,)
    )
    return cursor.fetchone()

def get_active_category(cursor, category_id):
    cursor.execute(
        "SELECT id FROM categories WHERE id = %s AND deleted = false;", (category_id,)
    )
    return cursor.fetchone()

def lambda_handler(event, context):
    try:
        category_id = int(event['pathParameters']['id'])
        item_id = int(event["queryStringParameters"]['itemID'])

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Category and Item ID\'s must be provided'})
        }

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                
                if not get_active_item(cursor, item_id):
                    return {
                        'statusCode': 400,
                        'body': json.dumps({
                            'error' : f'No Active Item found at ID: {item_id}'
                        })
                    }
                
                if not get_active_category(cursor, category_id):
                    return {
                        'statusCode': 400,
                        'body': json.dumps({
                            'error' : f'No Active Category found at ID: {category_id}'
                        })
                    }
                
                try:
                    cursor.execute(
                        """
                        INSERT INTO item_categories (item_id, category_id)
                        VALUES (%s, %s)
                        """,
                        (item_id, category_id))
                
                except psycopg2.errors.UniqueViolation:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({
                            'error' : f'Item at ID {item_id} is already added to Category with ID {category_id}'
                        })
                    }
                        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message' : f'Successfully added Item at ID {item_id} to Category at ID {category_id}'
            })
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', 'details' : str(e)})
        }

