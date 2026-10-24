from fastapi import FastAPI , HTTPException
import psycopg
import httpx

from app.llm import ask_direct
from app.schemas import AskRequest , DirectAnswer

from app.config import settings

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