from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running", "PORT": os.getenv("PORT")}

if __name__ == "__main__":
    import uvicorn
    # Must use platform PORT
    port = int(os.environ["PORT"])
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")