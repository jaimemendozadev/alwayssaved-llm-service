import uvicorn

if __name__ == "__main__":

    print("Starting app. 🚀")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
