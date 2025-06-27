import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("Starting app. 🚀")
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
