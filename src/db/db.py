import os
from psycopg2 import pool
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
import json

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

try:
    connection_pool = pool.ThreadedConnectionPool(
        minconn=1, maxconn=30, dsn=DATABASE_URL
    )
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
        if self.conn:
            register_vector(self.conn)
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
            (url,),
        )
        article = cur.fetchone()
        if article:
            return article
    return None


def get_top_n_chunks(query_embedding, n=20):
    with DBConnection() as conn:
        if not conn:
            print("Failed to get DB connection in get_top_n_chunks")
            return []  # Or raise an error
        cur = conn.cursor()

        # Add this line to ensure the vector type and operator are found
        cur.execute("SET search_path = onj, public;")

        # Modify the query to explicitly cast the parameter placeholder to vector
        query = """
            SELECT id, chunk_text, embedding <=> %s::vector AS similarity_score
            FROM content_chunks
            ORDER BY similarity_score ASC
            LIMIT %s;
        """
        try:
            # Parameters: embedding list first, then limit n
            cur.execute(query, (query_embedding, n))

            # fetch all the results
            fetched_rows = cur.fetchall()
            print(f"fetched {len(fetched_rows)} rows...")

            # return the results
            return [(row[0], row[1], row[2]) for row in fetched_rows]
        except Exception as e:
            print(f"Error executing query in get_top_n_chunks: {e}")
            import traceback  # Import for detailed traceback

            traceback.print_exc()  # Print detailed traceback
            conn.rollback()  # Rollback in case of error
            raise  # Re-raise the exception

def get_article(url):
    """
    Fetches an article from the database by its URL.
    
    Args:
        url (str): The URL of the article to fetch.
        
    Returns:
        dict: The article data if found, None otherwise.
    """
    with DBConnection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT chunk_text
            FROM public.content_chunks
            WHERE source_identifier = %s
            """,
            (url,),
        )
        article = cur.fetchone()
        chunk_object = json.loads(article[0]) if article else None
        if chunk_object:
            return chunk_object
        return None