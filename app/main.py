import httpx
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from app.config import BACKEND_URL, ORIGINS, SECRET_KEY
from app.routers.auth.router import router as auth_router
from app.routers.auth.services import UserDep

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


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    operation_id="proxy_all_methods",
)
async def proxy(path: str, request: Request, user: UserDep):
    url = f"{BACKEND_URL}/{path}"
    print(url)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Kopiowanie nagłówków, usuwamy te niepotrzebne
            excluded_headers = {
                "host",
                "content-length",
                "connection",
                "accept-encoding",
            }
            headers = {
                key: value
                for key, value in request.headers.items()
                if key.lower() not in excluded_headers
            }
            headers["Role"] = user.role

            body = await request.body()

            backend_response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params,
            )

        # Tworzymy odpowiedź przekazując status, nagłówki i treść
        return Response(
            content=backend_response.content,
            status_code=backend_response.status_code,
            headers={
                key: value
                for key, value in backend_response.headers.items()
                if key.lower()
                not in {"content-encoding", "transfer-encoding", "connection"}
            },
            media_type=backend_response.headers.get("content-type"),
        )

    except httpx.RequestError as exc:
        print(exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "Bad Gateway", "details": str(exc)},
        )

    except Exception as exc:
        print(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error", "details": str(exc)},
        )


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app="main:app", host="0.0.0.0", port=80, reload=True)
