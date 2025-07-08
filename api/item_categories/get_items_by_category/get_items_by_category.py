import json
import psycopg2
from db_connection import get_db_connection

def get_active_category(cursor, category_id):
    cursor.execute(
        "SELECT id FROM categories WHERE id = %s AND deleted = false;", (category_id,)
    )
    return cursor.fetchone()

def lambda_handler(event, context):
    try:
        category_id = int(event['pathParameters']['id'])

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Categories ID must be provided'})
        }

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                
                if not get_active_category(cursor, category_id):
                    return {
                        'statusCode': 400,
                        'body': json.dumps({
                            'error' : f'No Active Category found at ID: {category_id}'
                        })
                    }
                
                cursor.execute(
                    """
                    SELECT items.id, items.name, items.price 
                    FROM item_categories
                    INNER JOIN items ON item_categories.item_id = items.id
                    WHERE item_categories.category_id = %s AND items.deleted = FALSE;
                    """,
                    (category_id,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                items = [dict(zip(columns, row)) for row in rows]

        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', 'details' : str(e)})
        }

