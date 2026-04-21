from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import Agent

app = FastAPI(
    title="Smart Home Agentic RAG API",
    description="An API for querying a smart home environment using a Gemini-powered agent.",
    version="1.0.0"
)

# Initialize the agent
agent = Agent()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    reasoning_trace: list
    retrieved_context: str
    confidence_score: float

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Receives a user question, orchestrates the Gemini agent to generate a response,
    and returns a structured JSON output.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        response_data = agent.get_response(request.question)
        return QueryResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the Smart Home Agentic RAG API. Please use the /docs endpoint to see the API documentation."}
