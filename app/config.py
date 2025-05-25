import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

ORIGINS = os.getenv("ORIGIN").split(",") if os.getenv("ORIGIN") else ["*"]
ALGORITHM = "HS256"


# Lista backendów dla prostego load balancingu
SERVICE_INSTANCES = ["http://localhost:8001", "http://localhost:8002"]
