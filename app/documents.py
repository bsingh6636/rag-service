from pathlib import Path

def load_document() -> dict [str , str] :
    path = Path("data/docs/fastapi-features.md")
    content = path.read_text(encoding = "utf-8")

    if not content.strip() :
        raise ValueError("Document is empty")

    return {
        "title" : "FastAPI features" ,
        "source" :  "https://fastapi.tiangolo.com/features/",
        "content" : content 
    }