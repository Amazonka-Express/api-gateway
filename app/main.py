from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import ORIGINS, SECRET_KEY
from app.routers.auth.router import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth_router)


@app.get("/test", status_code=status.HTTP_200_OK)
async def test():
    return "test"


# def pick_service():
#     return random.choice(SERVICE_INSTANCES)


# @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
# async def proxy(path: str, request: Request):
#     backend_url = pick_service()
#     url = f"{backend_url}/{path}"

#     # Forward headers and data
#     client = httpx.AsyncClient()
#     req_headers = dict(request.headers)
#     body = await request.body()

#     response = await client.request(
#         request.method, url, headers=req_headers, content=body
#     )

#     return JSONResponse(status_code=response.status_code, content=response.json())


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app="main:app", host="0.0.0.0", port=80, reload=True)
