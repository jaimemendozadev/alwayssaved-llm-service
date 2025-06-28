import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.llm import llm_router

app = FastAPI()

APP_DOMAIN = os.getenv("APP_DOMAIN")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[APP_DOMAIN],  # <-- For development; restrict this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}
