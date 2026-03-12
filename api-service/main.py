from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from routers import webhook

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting api-service module...")
    yield
    logger.info("Shutting down api-service module...")

app = FastAPI(title="WhatsApp Webhook API", lifespan=lifespan)

# Include routers
app.include_router(webhook.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
