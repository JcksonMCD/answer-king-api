import os
import json
import psycopg2

def lambda_handler(event, context):
    try:
        item_id = int(event['pathParameters']['id'])
    except (KeyError, TypeError, ValueError):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid or missing ID in path'})
        }

    # Database operation
    try:
        with psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE items
                    SET deleted = TRUE
                    WHERE id = %s
                    RETURNING id;
                    """,
                    (item_id,)
                )
                deleted = cursor.fetchone()
                if not deleted:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': f'Item not found at ID: {item_id}'})
                    }

        return {
            'statusCode': 204,
            'body': json.dumps({'deleted_id': deleted[0]})
        }

    except psycopg2.Error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }