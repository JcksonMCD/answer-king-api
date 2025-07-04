import datetime
import os
import json
import psycopg2
from db_connection import get_db_connection

def json_default(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)

def lambda_handler(event, context):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, created_at FROM categories
                    WHERE deleted = false;
                    """
                    )
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                categories = [dict(zip(columns, row)) for row in rows]

        return {
            'statusCode': 200,
            'body': json.dumps(categories, default=json_default)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error'})
        }