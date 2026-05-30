import asyncio
import json
from typing import Dict

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from crew.runner import run_stock_analysis
from schemas.agent import RunRequest, RunResponse

router = APIRouter()

# run_id → asyncio.Queue (이벤트 스트림 버퍼)
_run_queues: Dict[str, asyncio.Queue] = {}


@router.post("/agents/run", response_model=RunResponse)
async def start_run(request: RunRequest):
    if request.runId in _run_queues:
        raise HTTPException(status_code=409, detail="run_id already exists")

    queue: asyncio.Queue = asyncio.Queue()
    _run_queues[request.runId] = queue

    loop = asyncio.get_running_loop()

    def emit(event_type: str, data: dict) -> None:
        """스레드풀 → 이벤트루프로 안전하게 이벤트 전달"""
        loop.call_soon_threadsafe(queue.put_nowait, {"event": event_type, "data": data})

    loop.run_in_executor(None, run_stock_analysis, request.question, emit)

    return RunResponse(status="started", runId=request.runId)


@router.get("/agents/stream/{run_id}")
async def stream_events(run_id: str):
    queue = _run_queues.get(run_id)
    if queue is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    async def event_generator():
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=300)
                except asyncio.TimeoutError:
                    yield {"event": "heartbeat", "data": ""}
                    continue

                yield {"event": item["event"], "data": json.dumps(item["data"], ensure_ascii=False)}

                if item["event"] in ("complete", "error"):
                    break
        finally:
            _run_queues.pop(run_id, None)

    return EventSourceResponse(event_generator())
