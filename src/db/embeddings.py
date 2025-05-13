from sentence_transformers import SentenceTransformer
from db.db import DBConnection

# Load a local transformer model once (384‑dim embeddings)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# dim = model.get_sentence_embedding_dimension()


def get_embedding(text: str) -> list[float]:
    """Compute a local embedding with sentence-transformers."""
    # model.encode returns a numpy array
    vec = model.encode(text, show_progress_bar=False)
    return vec.tolist()


def store_chunks(article: dict):
    """
    Combines all paragraph text from an article, prepends the title,
    computes a single embedding, and stores it as one chunk.
    """
    paragraph_texts = []
    for piece in article.get("pieces", []):
        if piece.get("type") == "paragraph":
            text = piece.get("text")
            if text:  # Ensure text is not None or empty
                paragraph_texts.append(text.strip())

    if not paragraph_texts:
        # print(f"No paragraph text found in article: {article.get('url', 'N/A')}")
        return  # Nothing to store if no paragraphs

    # Combine all paragraph texts with the title
    combined_text = " ".join(paragraph_texts)
    title = article.get("title", "").strip()
    text_to_embed = f"{title} {combined_text}".strip()
    date = article.get("date", "")
    if date:
        text_to_embed = f"{date} {text_to_embed}".strip()

    if not text_to_embed:
        # print(f"Empty text to embed after combining title and paragraphs for: {article.get('url', 'N/A')}")
        return  # Avoid storing empty strings

    # Compute a single embedding for the combined text
    try:
        embedding = get_embedding(text_to_embed)
    except Exception as e:
        print(f"Error computing embedding for {article.get('url', 'N/A')}: {e}")
        return  # Don't proceed if embedding fails

    # Store the single combined chunk
    with DBConnection() as conn:
        if not conn:
            print(
                f"Failed to get DB connection for storing chunk from {article.get('url', 'N/A')}"
            )
            return
        try:
            with conn.cursor() as cur:  # Use context manager for cursor
                # Set search path once per transaction if needed
                cur.execute("SET search_path = onj, public;")

                # Insert the single combined chunk
                cur.execute(
                    """
                    INSERT INTO content_chunks (chunk_text, embedding, source_identifier)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_identifier) DO NOTHING
                    """,
                    (
                        text_to_embed,
                        embedding,
                        article.get("url"),
                    ),
                )
            conn.commit()  # Commit the transaction
            # print(f"Stored combined chunk for: {article.get('url', 'N/A')}")
        except Exception as e:
            print(f"Error storing chunk for {article.get('url', 'N/A')} in DB: {e}")
            conn.rollback()  # Rollback on error
        # No need for cur.close() or conn.close() due to 'with' statements
