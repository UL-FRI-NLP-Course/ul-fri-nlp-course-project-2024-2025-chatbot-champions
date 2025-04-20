import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

try:
    connection_pool = pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=30,
        dsn=DATABASE_URL
    )
    if connection_pool:
        print("Connection pool created successfully.")
except Exception as e:
    print("Error creating connection pool:", e)
    connection_pool = None

def get_connection():
    try:
        if connection_pool:
            return connection_pool.getconn()
    except Exception as e:
        print("Error obtaining connection:", e)
    return None

def release_connection(conn):
    try:
        if connection_pool and conn:
            connection_pool.putconn(conn)
    except Exception as e:
        print("Error releasing connection:", e)

class DBConnection:
    """Context manager for database connections."""
    def __enter__(self):
        self.conn = get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        release_connection(self.conn)

def get_article(url):
    with DBConnection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id
            FROM onj.articles
            WHERE url = %s
            """,
            (url,)
        )
        article = cur.fetchone()
        if article:
            return article
    return None