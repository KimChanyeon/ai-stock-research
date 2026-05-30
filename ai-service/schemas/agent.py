from pydantic import BaseModel


class RunRequest(BaseModel):
    runId: str
    question: str


class RunResponse(BaseModel):
    status: str
    runId: str
