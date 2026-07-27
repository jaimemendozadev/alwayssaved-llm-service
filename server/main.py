from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.convos import convos_router
from server.utils.app_domains import APP_DOMAINS

app = FastAPI()

print(f"APP_DOMAINS {APP_DOMAINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_DOMAINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convos_router, prefix="/llm-api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"Hello": "World"}
