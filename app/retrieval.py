import logging
import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from app.config import settings
from app.embeddings import embed_text

logger = logging.getLogger(__name__)


def search_chunks(
    question: str,
    top_k: int = 3,
    similarity_threshold: float | None = None,
) -> list[dict]:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10")

    threshold = (
        similarity_threshold
        if similarity_threshold is not None
        else settings.similarity_threshold
    )

    query_text = f"task :  search result | query:{question}"
    query_vector = Vector(embed_text(query_text))

    with psycopg.connect(
        settings.database_url,
        connect_timeout=5,
        row_factory=dict_row,
    ) as conn:
        register_vector(conn)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    c.id as chunk_id,
                    c.content,
                    d.title,
                    d.source,
                    1 - (c.embedding <=> %s) AS similarity
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE 1 - (c.embedding <=> %s) >= %s
                ORDER BY c.embedding <=> %s
                LIMIT %s
                """,
                (query_vector, query_vector, threshold, query_vector, top_k),
            )

            results = cur.fetchall()
            logger.info(
                "Retrieved %d chunks above similarity threshold %.2f (top_k=%d)",
                len(results),
                threshold,
                top_k,
            )
            return results
