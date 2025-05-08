import random

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.config import SECRET_KEY, SERVICE_INSTANCES
from app.routers.auth.router import router as auth_router
from app.routers.auth.services import user_dependency

origins = ["*", "http://localhost:3000"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth_router)


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")

    return {"user": user}


@app.get("/test", status_code=status.HTTP_200_OK)
async def test():
    return "test"


def pick_service():
    return random.choice(SERVICE_INSTANCES)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    backend_url = pick_service()
    url = f"{backend_url}/{path}"

    # Forward headers and data
    client = httpx.AsyncClient()
    req_headers = dict(request.headers)
    body = await request.body()

    response = await client.request(
        request.method, url, headers=req_headers, content=body
    )

    return JSONResponse(status_code=response.status_code, content=response.json())


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app="main:app", host="0.0.0.0", port=80, reload=True)
