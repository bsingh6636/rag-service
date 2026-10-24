CREATE EXTENSION IF NOT EXISTS vector ;

CREATE TABLE DOCUMENTS (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE CHUNKS (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT ,
    embedding VECTOR(1536) NOT NULL,
    UNIQUE (document_id , chunk_index)
);