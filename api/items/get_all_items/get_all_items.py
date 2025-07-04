import os
import json
import psycopg2
from db_connection import get_db_connection

def lambda_handler(event, context):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, price, description FROM items WHERE deleted = FALSE;")
                rows = cursor.fetchall()
                items = []
                for row in rows:
                    item = {}
                    for i, column in enumerate(cursor.description):
                        item[column[0]] = str(row[i])
                    items.append(item)

        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', "message" : str(e)})
        }