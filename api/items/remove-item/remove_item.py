import os
import json
import psycopg2
from db_connection import get_db_connection

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
        with get_db_connection as conn:
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