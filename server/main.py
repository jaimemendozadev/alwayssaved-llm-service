from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.llm import llm_router

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],  # <-- For development; restrict this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}
