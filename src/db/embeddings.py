from sentence_transformers import SentenceTransformer
from db.db import DBConnection
from datetime import datetime
import json

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
    # Add all metadata to the text (title, subtitle, recap, section, author, date, subcategory, url)
    subtitle = article.get("subtitle", "").strip()
    recap = article.get("recap", "").strip()
    section = article.get("section", "").strip()
    author = article.get("author", "").strip()
    date = article.get("date", "").strip()
    subcategory = article.get("subcategory", "").strip()
    url = article.get("url", "").strip()
    iso_date = ""
    if date:
        try:
            # Remove any extra spaces and parse flexible d. m. yyyy format
            date_clean = date.replace(" ", "")
            parsed_date = datetime.strptime(date_clean, "%d.%m.%Y")
        except ValueError:
            parsed_date = None
        if parsed_date:
            iso_date = parsed_date.date().isoformat()
            article["iso_date"] = iso_date
    object_string = json.dumps(article, ensure_ascii=False)
    text_to_embed = object_string
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

def convert_article_to_chunk(article_json):
    """
    Convert a JSON article into a flattened context chunk string
    using pieces parsed from HTML (paragraphs, images, tables).
    """
    # Extract metadata fields with defaults
    title = article_json.get('title', '').strip()
    subtitle = article_json.get('subtitle', '').strip()
    subcategory = article_json.get('subcategory', '').strip()
    date = article_json.get('iso_date') or article_json.get('date', '').strip()
    url = article_json.get('url', '').strip()
    author = article_json.get('author', '').strip()
    section = article_json.get('section', '').strip()
    recap = article_json.get('recap', '').strip()

    # Build CONTENT by iterating over pre-parsed pieces
    content_lines = []
    for piece in article_json.get('pieces', []):
        ptype = piece.get('type')
        if ptype == 'paragraph':
            text = piece.get('text', '').strip()
            if text:
                content_lines.append(text)
        elif ptype == 'image':
            caption = piece.get('caption', '').strip()
            content_lines.append(f"[IMAGE: {caption}]")
        elif ptype == 'table':
            rows = piece.get('content', [])
            # format as table text
            table_lines = ["[TABLE:]"]
            for row in rows:
                table_lines.append(" | ".join(cell.strip() for cell in row))
            table_lines.append("[END TABLE]")
            content_lines.extend(table_lines)

    content = "\n".join(content_lines)

    # Construct the final chunk string
    chunk = (
        f"[DATE: {date}]\n"
        f"TITLE: {title}\n"
        f"SUBTITLE: {subtitle}\n"
        f"SUBCATEGORY: {subcategory}\n"
        f"URL: {url}\n"
        f"AUTHOR: {author}\n"
        f"SECTION: {section}\n"
        f"RECAP: {recap}\n"
        f"CONTENT:\n{content}"
    )
    return chunk
