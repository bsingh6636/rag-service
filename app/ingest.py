import logging
import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from app.chunking import chunk_text, count_tokens
from app.config import settings
from app.documents import load_document, load_documents
from app.embeddings import embed_text

logger = logging.getLogger(__name__)


def ingest_document(document: dict | None = None) -> dict:
    if document is None:
        document = load_document()

    chunks = chunk_text(document["content"])

    if not chunks:
        raise ValueError(f"Document '{document.get('title')}' provided no chunks")

    prepared = []

    for index, chunk in enumerate(chunks):
        logger.info(
            "Embedding chunk %d/%d for '%s'",
            index + 1,
            len(chunks),
            document.get("title", "Untitled"),
        )

        embedding_input = f"title : {document['title'] }| text : {chunk}"
        vector = embed_text(embedding_input)

        prepared.append((index, chunk, count_tokens(chunk), Vector(vector)))

    with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
        register_vector(conn)

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (source, title)
                VALUES (%s, %s)
                ON CONFLICT (source)
                DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """,
                (document["source"], document["title"]),
            )
            document_id = cur.fetchone()[0]

            cur.execute(
                "DELETE FROM chunks WHERE document_id = %s",
                (document_id,),
            )

            cur.executemany(
                """
                INSERT INTO chunks
                (document_id, chunk_index, content, token_count, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [(document_id, *row) for row in prepared],
            )

    logger.info(
        "Ingested document_id=%d ('%s') with %d chunks",
        document_id,
        document.get("title"),
        len(prepared),
    )
    return {
        "document_id": document_id,
        "chunks_saved": len(prepared),
    }


def ingest_corpus() -> dict:
    documents = load_documents()
    logger.info("Starting ingestion of %d documents into corpus", len(documents))

    details = []
    total_chunks = 0
    last_doc_id = None

    for doc in documents:
        result = ingest_document(doc)
        details.append(
            {
                "document_id": result["document_id"],
                "source": doc["source"],
                "title": doc.get("title"),
                "chunks_saved": result["chunks_saved"],
            }
        )
        total_chunks += result["chunks_saved"]
        last_doc_id = result["document_id"]

    logger.info(
        "Corpus ingestion complete: %d documents, %d total chunks saved",
        len(documents),
        total_chunks,
    )
    return {
        "document_id": last_doc_id,
        "chunks_saved": total_chunks,
        "documents_ingested": len(documents),
        "details": details,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(ingest_corpus())
