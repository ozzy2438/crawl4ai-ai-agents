-- Enable the pgvector extension to work with embedding vectors
CREATE EXTENSION IF NOT EXISTS vector;

-- Create crawled_data table
CREATE TABLE IF NOT EXISTS crawled_data (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    url text NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    embedding vector(384)  -- For storing text embeddings
);

-- Create a function to update embeddings
CREATE OR REPLACE FUNCTION match_crawled_data (
    query_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id uuid,
    url text,
    content text,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        crawled_data.id,
        crawled_data.url,
        crawled_data.content,
        1 - (crawled_data.embedding <=> query_embedding) AS similarity
    FROM crawled_data
    WHERE 1 - (crawled_data.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
$$;

-- Create an index for faster similarity searches
CREATE INDEX ON crawled_data
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);