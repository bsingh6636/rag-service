import psycopg 
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from app.config import settings
from app.embeddings import embed_text

def search_chunks ( question : str , top_k : int = 3 ) -> list[dict] :
    if not question.strip():
        raise ValueError("QUestion cannnot be empty")

    if not 1 <= top_k <= 10 :
        raise ValueError("top_k must be between 1 and 10")

    query_text = f"task :  search result | query:{question}"
    query_vector = Vector(embed_text(query_text))

    with psycopg.connect(
        settings.database_url,
        connect_timeout = 5 ,
        row_factory = dict_row
    ) as conn :
        register_vector(conn)

        with conn.cursor() as cur :
            cur.execute(
                """
                SELECT 
                    c.id as chunk_id,
                    c.content,
                    d.title,
                    d.source,
                    1 - (c.embedding <=> %s) AS similarity
                FROM chunks c
                JOIN documents d on d.id = c.document_id
                ORDER BY c.embedding <=> %s
                LIMIT %s
                """,
                (query_vector , query_vector , top_k)
            )

            return cur.fetchall()