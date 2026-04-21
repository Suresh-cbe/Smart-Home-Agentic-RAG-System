from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import Agent

app = FastAPI()
agent = Agent()


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
async def query(req: QueryRequest):
    if not req.question:
        raise HTTPException(status_code=400, detail="Empty question")

    return agent.get_response(req.question)