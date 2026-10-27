---
title: FastAPI Dependency Injection
source: https://fastapi.tiangolo.com/tutorial/dependencies/
---

# Dependencies - First Steps

FastAPI has a very powerful but intuitive **Dependency Injection** system.

It is designed to be very simple to use, and to make it very easy for any developer to integrate other components with **FastAPI**.

## What is "Dependency Injection"

**"Dependency Injection"** means, in programming, that there is a way for your code (in this case, your *path operation functions*) to declare things that it requires to work and use: "dependencies".

And then, that system (in this case **FastAPI**) will take care of doing whatever is needed to provide your code with those needed dependencies ("inject" the dependencies).

This is very useful when you need to:
* Have shared logic (the same code logic over and over).
* Share database connections.
* Enforce security, authentication, and role requirements.
* And many other things...

All these, while minimizing code repetition.

## Declaring a Dependency with Depends

To declare a dependency, you import `Depends` from `fastapi` and use it as the default value of a function parameter in your path operation.

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

FastAPI will call the dependency function `common_parameters` with the right parameters from the request, take the result, and assign it to `commons`.

## Sub-dependencies and Hierarchical Dependencies

You can declare dependencies that themselves declare dependencies.

FastAPI takes care of resolving them in the correct order, building a dependency tree or directed acyclic graph (DAG).

```python
def query_extractor(q: str | None = None):
    return q

def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q
```

If one of your dependencies is declared multiple times in different places of the same path operation, FastAPI will know to call that dependency only once per request and cache the return value for that request, optimizing execution time.

## Dependencies with yield (Cleanup and Teardown)

FastAPI supports dependencies that do some extra steps after finishing.

To do this, use `yield` instead of `return`, where the code before `yield` is executed before the path operation, and the code after `yield` is executed after the response is sent.

This is ideal for database sessions and resource cleanup:

```python
async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
```

The `finally` block guarantees that the database session is closed even if an exception occurs during the handling of the request.

## Dependencies in Path Operation Decorators

In some cases, you don't really need the return value of a dependency inside your path operation function, but you still need the dependency to be executed (for example, for authentication or header validation).

For these cases, you can use a `dependencies` parameter in the path operation decorator:

```python
@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Portal Gun"}]
```

## Global Dependencies

You can also add dependencies to an entire `FastAPI` app or `APIRouter`:

```python
app = FastAPI(dependencies=[Depends(verify_token)])
```

Every single request to the app will execute `verify_token` before the path operation is called.

## Dependency Overrides for Testing

When testing FastAPI applications, you frequently need to override dependencies to use mock databases, test authentication tokens, or stub external services.

FastAPI provides `app.dependency_overrides` for this exact purpose:

```python
async def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

After testing, you can clean up the overrides by setting `app.dependency_overrides = {}`.
