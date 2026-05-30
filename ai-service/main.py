from core.logging_config import setup_logging

setup_logging()

import logging

from fastapi import FastAPI

from routers.agents import router as agents_router

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Stock Research Service")
app.include_router(agents_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}


logger.info("AI Stock Research Service started")
