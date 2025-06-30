import os
import json
import psycopg2

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
        with psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Check item exists and isnt deleted
                cursor.execute(
                    """
                    SELECT id FROM items
                    WHERE id = %s
                    """,
                    (item_id,))
                
                if not cursor.fetchone():
                    return {
                        'statusCode': 400,
                        'body': json.dumps({
                            'error' : f'No Active Item found at ID: {item_id}'
                        })
                    }
                
                # Check category exists and isnt deleted
                cursor.execute(
                    """
                    SELECT id FROM categories
                    WHERE id = %s
                    AND deleted = false;
                    """,
                    (category_id,))
                
                if not cursor.fetchone():
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

