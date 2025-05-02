from sentence_transformers import CrossEncoder  # Uncommented

# --- Load the reranker model ---
# Load a cross-encoder model once (example: ms-marco-MiniLM-L-6-v2 is good for passage ranking)
try:
    # Using a smaller, potentially faster model if available, or stick to ms-marco
    cross_encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
except Exception as e:
    print(f"Error loading CrossEncoder model: {e}")
    print("Reranking will not be performed. Returning original chunks.")
    cross_encoder_model = None  # Ensure model is None if loading failed
# --- End Model Loading ---


def rerank_chunks(query: str, chunks: list[tuple], top_n: int = 3) -> list[tuple]:
    """
    Reranks the retrieved chunks based on their relevance to the query
    using a CrossEncoder model.

    Args:
        query: The user's original query.
        chunks: A list of tuples from the initial retrieval
                (e.g., [(id, chunk_text, initial_score), ...]).
        top_n: The number of top chunks to return after reranking.

    Returns:
        A list of the top_n tuples, sorted by the CrossEncoder score,
        in the format (id, chunk_text, reranker_score).
    """
    if (
        not chunks or cross_encoder_model is None
    ):  # Check if model loaded and chunks exist
        # If no model or no chunks, return original chunks (or top_n of them)
        return chunks[:top_n]

    print(f"Reranker received {len(chunks)} chunks. Performing reranking...")

    # --- Reranking Logic ---
    # 1. Format input: pairs of [query, chunk_text]
    #    Assuming chunk tuple is (id, chunk_text, initial_score)
    chunk_texts = [chunk[1] for chunk in chunks]
    query_chunk_pairs = [[query, text] for text in chunk_texts]

    # 2. Get scores from the cross-encoder model
    #    predict() returns numpy array of scores
    scores = cross_encoder_model.predict(query_chunk_pairs, show_progress_bar=False)

    # 3. Combine original chunk data with new scores
    reranked_data = []
    for i, chunk in enumerate(chunks):
        # Keep original id, text, and add the new reranker score
        reranked_data.append((chunk[0], chunk[1], scores[i]))

    # 4. Sort the chunks based on the new scores (descending)
    reranked_data.sort(key=lambda x: x[2], reverse=True)

    # 5. Return the top N reranked chunks
    return reranked_data[:top_n]
