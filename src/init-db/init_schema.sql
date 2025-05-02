-- init_schema.sql
-- DDL script to initialize the database schema for the RAG project
-- using PostgreSQL and pgvector.

-- Make sure the script stops on any error
\set ON_ERROR_STOP on

-- Enable the pgvector extension if it's not already enabled.
-- This is necessary to use the VECTOR data type and its functions.
CREATE EXTENSION IF NOT EXISTS vector;

-- Optional: Drop the table if it exists, useful for resetting during development.
-- Be CAREFUL using DROP TABLE in production environments!
-- DROP TABLE IF EXISTS content_chunks;

-- Create the main table to store text chunks and their embeddings.
CREATE TABLE IF NOT EXISTS content_chunks (
    -- Primary key for uniquely identifying each chunk
    id SERIAL PRIMARY KEY,

    -- The actual text content of the chunk. Cannot be null.
    chunk_text TEXT NOT NULL,

    -- The vector embedding for this specific text chunk. Cannot be null.
    -- IMPORTANT: Replace [YOUR_EMBEDDING_DIMENSION] with the correct dimension
    -- for your embedding model (e.g., 384, 768, 1536, 3072, etc.).
    embedding VECTOR(384) NOT NULL,

    -- Metadata: The source URL or identifier from where the text originated.
    -- Can be null if the source is unknown or not applicable.
    source_identifier TEXT,

    -- Metadata: Timestamp indicating when this chunk was created or ingested.
    -- Defaults to the time the row was inserted.
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- TODO: add this
    -- Consider adding a FOREIGN KEY constraint if you have a separate 'documents' table.
    -- document_id INT NOT NULL, -- Or BIGINT, UUID, or TEXT depending on your document ID strategy

    -- The sequential index (0-based or 1-based) of this chunk within the original document.
    -- chunk_index INT NOT NULL,

    -- Metadata: Flexible storage for any other relevant information
    -- (e.g., document ID, page number, specific tags). JSONB is efficient.
    metadata JSONB
);

-- Create an index on the embedding column for efficient similarity search.
-- Using HNSW (Hierarchical Navigable Small World) index with cosine distance,
-- which is often a good choice for text embeddings.
-- Other options include IVFFlat index or different distance metrics (vector_l2_ops, vector_ip_ops).
-- Index creation can take time for large tables.
-- The name 'idx_content_chunks_embedding_hnsw_cosine' is descriptive.
CREATE INDEX IF NOT EXISTS idx_content_chunks_embedding_hnsw_cosine
ON content_chunks
USING HNSW (embedding vector_cosine_ops);

-- Optional: Add comments to the table and columns for better documentation
COMMENT ON TABLE content_chunks IS 'Stores text chunks, their vector embeddings, and associated metadata for RAG.';
COMMENT ON COLUMN content_chunks.chunk_text IS 'The actual text content of the chunk.';
COMMENT ON COLUMN content_chunks.embedding IS 'Vector embedding of the chunk_text. Dimension must match the embedding model.';
COMMENT ON COLUMN content_chunks.source_identifier IS 'URL, filename, or other identifier for the source of the text chunk.';
COMMENT ON COLUMN content_chunks.created_at IS 'Timestamp when the chunk was added to the database.';
COMMENT ON COLUMN content_chunks.metadata IS 'Arbitrary JSONB metadata associated with the chunk (e.g., page number, document tags).';


-- End of script message
\echo 'Database schema initialization complete.'
\echo 'Remember to replace [YOUR_EMBEDDING_DIMENSION] in the VECTOR type definition if you haven't already!'