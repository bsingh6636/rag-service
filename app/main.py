from fastapi import FastAPI
import psycopg

from app.config import settings

app = FastAPI(title = "RAG Service")

@app.get('/health')
def health():
    with psycopg.connect(settings.database_url , connect_timeout = 5 ) as conn:
        with conn.cursor() as cur :
            cur.execute("SELECT 1")
            cur.fetchone()
    
    return { "status" : "ok" , "db" : "ok"  }