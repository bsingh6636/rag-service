from fastapi import FastAPI , HTTPException
import psycopg
import httpx
import logging

from app.llm import ask_direct
from app.schemas import AskRequest , DirectAnswer, RagAnswer, IngestResult
from app.rag import ask_rag
from app.ingest import ingest_document


from app.config import settings

logging.basicConfig(
    level = logging.INFO ,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s" 
)

app = FastAPI(title = "RAG Service")

@app.get('/health')
def health():
    with psycopg.connect(settings.database_url , connect_timeout = 5 ) as conn:
        with conn.cursor() as cur :
            cur.execute("SELECT 1")
            cur.fetchone()
    
    return { "status" : "ok" , "db" : "ok"  }

@app.post("/ask-direct" , response_model = DirectAnswer )
def ask_direct_route( body : AskRequest ) :
    try : 
        return ask_direct(body.question)
    except httpx.TimeoutException : 
        raise HTTPException(
            status_code = 504 , detail = "MWAPI timed out"
        ) from None
    except httpx.HTTPError:
        raise HTTPException (
            status_code = 502 , detail = "MWAPI request failed"
        ) from None
    except (ValueError, KeyError, TypeError) :
        raise HTTPException(
            status_code=502, detail="MWAPI returned an invalid answer"
        ) from None

@app.post("/ask" , response_model = RagAnswer)
def ask_route(body : AskRequest) :
    if not body.question.strip() :
        raise HTTPException(
            status_code = 422 , 
            detail = "Question can not be blank"
        )

    try : 
        return ask_rag(body.question)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="AI provider timed out"
        ) from None

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502, detail="AI provider request failed"
        ) from None

    except psycopg.Error:
        raise HTTPException(
            status_code=503, detail="Database request failed"
        ) from None

    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=502, detail="Invalid AI response or citation"
        ) from None

@app.post("/ingest", response_model = IngestResult)
def ingest_route() :
    try :
        return ingest_document()
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Embedding provider timed out",
        ) from None

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Embedding provider request failed",
        ) from None

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database request failed",
        ) from None
    
