from pydantic import BaseModel


class RunRequest(BaseModel):
    run_id: str
    question: str


class RunResponse(BaseModel):
    status: str
    run_id: str
