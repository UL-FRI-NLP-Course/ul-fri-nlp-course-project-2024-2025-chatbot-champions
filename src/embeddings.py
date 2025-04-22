from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from db import DBConnection

# Load a local transformer model once (384‑dim embeddings)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

dim = model.get_sentence_embedding_dimension()
print("Embedding dimension:", dim)

def get_embedding(text: str) -> list[float]:
    """Compute a local embedding with sentence-transformers."""
    # model.encode returns a numpy array
    vec = model.encode(text, show_progress_bar=False)
    return vec.tolist()

def store_pieces(meta: dict, pieces: list[dict]):
    with DBConnection() as conn:
        cur = conn.cursor()
        cur.execute("SET search_path = onj, public;")
        register_vector(conn)
        cur.execute(
            """
            INSERT INTO articles (title, subtitle, recap, published_at, section, author, url, subcategory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                meta["title"],
                meta["subtitle"],
                meta["recap"],
                meta["published_at"],
                meta["section"],
                meta["author"],
                meta["url"],
                meta["subcategory"]
            )
        )
        article_id = cur.fetchone()[0]
        for piece in pieces:
            text = ""
            if piece["type"] == "paragraph":
                text = piece["text"]
            elif piece["type"] == "image":
                text = piece["caption"]
            elif piece["type"] == "table":
                text = "\n".join(["\t".join(row) for row in piece["content"]])
            else:
                continue
            emb  = get_embedding(text)
            cur.execute(
                """
                INSERT INTO article_pieces (piece_type, content, embedding, article_id)
                VALUES (%s, %s, %s, %s)
                """,
                (piece["type"], text, emb, article_id)
            )

        conn.commit()
        cur.close()
        conn.close()
