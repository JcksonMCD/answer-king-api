import os
import json
import psycopg2
import decimal

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return str(obj)

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
        with psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        ) as conn:
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
            'body': json.dumps(items, default=decimal_default)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', 'details' : str(e)})
        }

