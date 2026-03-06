from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running", "PORT": os.getenv("PORT")}

# Use platform-assigned port
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")