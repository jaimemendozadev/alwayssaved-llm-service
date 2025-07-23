import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("Starting app. 🚀")
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
