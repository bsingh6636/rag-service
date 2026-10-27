---
title: FastAPI Security and Authentication
source: https://fastapi.tiangolo.com/tutorial/security/
---

# Security and Authentication in FastAPI

FastAPI provides complete, standards-compliant security tools based on **OpenAPI** and **OAuth2**.

## Security Schemes and Standards

FastAPI includes built-in security utilities for the most common security mechanisms defined in the OpenAPI specification:
* **HTTP Basic**: Standard HTTP authentication where credentials are sent as Base64 encoded headers.
* **OAuth2**: The industry standard protocol for authorization, including password flow, authorization code flow, and bearer token verification.
* **API Key**: API keys passed in headers (`X-API-Key`), query parameters, or cookie values.
* **OpenID Connect**: Automatic discovery of authentication specifications using OpenID Connect configuration.

## OAuth2 with Password Flow and Bearer Tokens

The most common security pattern for web APIs is the **OAuth2 password flow** with JSON Web Tokens (JWT).

In this flow:
1. The frontend client sends the username and password in a `POST` request with form data to the `/token` endpoint using `OAuth2PasswordRequestForm`.
2. The server verifies the credentials against the database.
3. If credentials are valid, the server returns an access token, typically a signed JWT.
4. For subsequent requests, the frontend sends the token in the `Authorization: Bearer <token>` header.
5. FastAPI extracts the token using `OAuth2PasswordBearer` and verifies it.

```python
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## Password Hashing with Passlib and Bcrypt

Passwords should never be stored in plaintext. FastAPI tutorials recommend using **Passlib** with the **Bcrypt** algorithm for password hashing and verification.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
```

## JSON Web Tokens (JWT)

JSON Web Tokens (JWT) encode claims and user identifiers inside a digitally signed, URL-safe string.

Key properties of JWTs in FastAPI:
* Signed using a cryptographic secret key and algorithms such as **HS256** (HMAC-SHA256) or **RS256** (asymmetric RSA).
* Contain standard claims such as `sub` (subject identifier, e.g. username), and `exp` (expiration timestamp).
* Decoded and verified using libraries like `python-jose` or `PyJWT`.
* Self-contained: The API server does not need to look up session state in a centralized session store for every request.

## Current User Dependency

By combining `OAuth2PasswordBearer` with FastAPI's dependency injection, you create a `get_current_user` dependency that automatically decodes the JWT and fetches the user object.

```python
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user
```

Any endpoint needing authentication simply adds `current_user: Annotated[User, Depends(get_current_user)]`.

## Security Scopes

FastAPI supports **OAuth2 scopes** for fine-grained permissions (e.g., `items:read`, `items:write`, `admin`).

You can use `SecurityScopes` to check that the incoming token possesses the required permission scopes before executing the endpoint.
