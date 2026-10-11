import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    # When run as module (docker/uvicorn)
    from api import router as api_router
except ImportError:
    # When run directly
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from api import router as api_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Video Generator")
app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
