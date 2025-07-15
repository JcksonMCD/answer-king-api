import os
import psycopg2
from contextlib import contextmanager
import psycopg2.pool
from .logger import logger

_connection_pool = None

def init_connection_pool(minconn=1, maxconn=3):
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn,
            maxconn,
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            dbname=os.environ['DB_NAME']
        )
    
    return _connection_pool

@contextmanager
def get_db_connection():
    pool = init_connection_pool()
    conn = pool.getconn()

    try:
        yield conn
    except psycopg2.Error as e:
        logger.error(f"DB error, discarding connection: {e}")
        pool.putconn(conn, close=True)
        raise
    else:
        pool.putconn(conn)