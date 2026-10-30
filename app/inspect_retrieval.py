from app.retrieval import search_chunks

questions: list[str] = [
    "Which API documentation interfaces does FastAPI include?",
    "What retry count and backoff does FastAPI automatically apply to failed BackgroundTasks?",
    "What temperature should I use to bake a chocolate cake?",
]

for question in questions :
    print("\nQUESTION:", question)

    matches = search_chunks(
        question,
        top_k = 3 ,
        similarity_threshold= -1.0
    )

    for match in matches :
        print(
            round(match["similarity"] ,4 ),
            match["content"].splitlines()[0],
        )