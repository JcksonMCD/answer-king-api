import os
import json
import psycopg2
from db_connection import get_db_connection

def lambda_handler(event, context):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO orders
                    DEFAULT VALUES
                    RETURNING id, status, total, 
                    created_at;
                    """,
                    )
                
                order_id, order_status, order_total, created_at = cursor.fetchone()
                conn.commit()
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'id': order_id,
                'status' : order_status,
                'total' : str(order_total),
                'created_at': created_at.isoformat()
            })
        }
        
    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', "message" : str(e)})
        }