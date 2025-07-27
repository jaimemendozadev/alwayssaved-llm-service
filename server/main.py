import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.convos import convos_router
from server.utils.aws.ssm import get_secret

app = FastAPI()

PYTHON_MODE = os.getenv("PYTHON_MODE", "DEVELOPMENT")

APP_DOMAIN = (
    get_secret("/alwayssaved/FASTAPI_PRODUCTION_APP_DOMAIN")
    if PYTHON_MODE == "PRODUCTION"
    else os.getenv("FASTAPI_DEVELOPMENT_APP_DOMAIN", "")
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[APP_DOMAIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convos_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"Hello": "World"}
