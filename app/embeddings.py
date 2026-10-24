import httpx
from app.config import settings

def embed_text(text : str) -> list[float]:
    if not text.strip():
        raise ValueError('Cannot embed empty text')
    
    url = (
         "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.embedding_model}:embedContent"
    )

    response = httpx.post(
        url,
        headers = {"x-goog-api-key" : settings.gemini_api_key } ,
        json = {
            "content" : {
                "parts" : [{"text" : text }]
            },
            "outputDimensionality" : settings.embedding_dim
        },
        timeout = 30
    )

    response.raise_for_status()

    data = response.json()
    vector = data["embedding"]["values"]

    if len(vector) !=settings.embedding_dim :
        raise ValueError(
            f"Expected {settings.embedding_dim} dimensions ,"
            f"Received {len(vector)}"
        )
    return vector 