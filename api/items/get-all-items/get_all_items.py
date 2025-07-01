import os
import json
import psycopg2

def lambda_handler(event, context):
    try:
        with psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, price, description FROM items WHERE deleted = FALSE;")
                rows = cursor.fetchall()
                items = []
                for row in rows:
                    item = {}
                    for i, column in enumerate(cursor.description):
                        item[column.name] = str(row[i])
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