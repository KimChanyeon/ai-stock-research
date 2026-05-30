from fastapi import FastAPI

from routers.agents import router as agents_router

app = FastAPI(title="AI Stock Research Service")

app.include_router(agents_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
