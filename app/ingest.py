
import logging ;

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from app.chunking import chunk_text , count_tokens 
from app.config import settings
from app.documents import load_document
from app.embeddings import embed_text

logger = logging.getLogger(__name__)

def ingest_document() -> dict :
    document = load_document()
    chunks = chunk_text(document["content"])

    if not chunks :
        raise ValueError("Document provided no chubks")

    prepared = []

    for index , chunk in enumerate(chunks) :
        logger.info("Embedding chunk %d%d",  index + 1 , len(chunks) )

        embedding_input = (
            f"title : {document['title'] }| text : {chunk}"
        )

        vector = embed_text(embedding_input)

        prepared.append(
            (index , chunk , count_tokens(chunk) , Vector(vector) )
        )
    with psycopg.connect(settings.database_url , connect_timeout = 5) as conn :
        register_vector(conn)

        with conn.cursor() as cur :
            cur.execute(
                """
                INSERT INTO documents (source , title)
                VALUES (%s, %s)
                ON CONFLICT (source)
                DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """,
                (document["source"] , document["title"] ),
            )
            document_id = cur.fetchone()[0]

            cur.execute(
                "DELETE FROM chunks where document_id = %s", (document_id,),
            )

            cur.executemany(
                """
                INSERT INTO chunks
                (document_id , chunk_index , content, token_count , embedding)
                VALUES (%s, %s ,%s , %s , %s)
                """,
                [(document_id, *row) for row in prepared ],
            )

    return {
        "document_id" : document_id ,
        "chunks_saved" : len(prepared),
    }

if __name__ == "__main__" :
    logging.basicConfig(level = logging.INFO)
    print(ingest_document())