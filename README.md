# 🏠 Smart Home Agentic RAG System

An advanced **Agentic RAG (Retrieval-Augmented Generation)** system for querying a smart home environment using **Neo4j (Graph DB)** and **Google Gemini (LLM)**.

This system allows users to ask natural language questions and get **accurate, grounded responses** based on real device data.

---

## 🚀 Features

- ✅ Natural Language Query API (FastAPI)
- ✅ Graph-based retrieval using Neo4j
- ✅ Semantic search using vector embeddings
- ✅ Hybrid RAG (Cypher + Vector Search)
- ✅ Tool-based agent architecture
- ✅ Multi-step reasoning loop
- ✅ Rule-based guardrails (safety + validation)
- ✅ Explainable reasoning trace
- ✅ Confidence scoring
- ✅ Dockerized setup (API + Database)

---

## 🧠 Architecture


User Query
↓
Agent (Tool Selection)
↓
[Cypher Query] OR [Semantic Search]
↓
Neo4j (Graph + Vector Index)
↓
Retrieved Context
↓
Gemini LLM (Response Generation)
↓
Final Answer + Reasoning Trace


---

## 🛠 Tech Stack

- **Backend**: FastAPI
- **LLM**: Google Gemini (gemini-2.5-flash-lite)
- **Database**: Neo4j (Graph + Vector Index)
- **Embeddings**: gemini-embedding-001
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.11

---

## 📁 Project Structure


app/
├── main.py # FastAPI entry point
├── agent.py # Core AI agent logic
├── database.py # Neo4j + embeddings
├── tools.py # Tool abstraction layer
├── schemas.py # Request/response models
data/
├── seed_db.py # Database seeding
tests/
├── test_agent.py # Testing scripts
.env
docker-compose.yml
Dockerfile
requirements.txt
README.md

## ⚙️ Setup Instructions

### 🔹 1. Clone Repository

git clone <your-repo-url>
cd smart-home-agentic-rag
🔹 2. Create .env file
GOOGLE_API_KEY=your_api_key
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
🔹 3. Run with Docker
docker-compose up --build
🔹 4. Access Services
API Docs (Fast API) → http://localhost:8000/docs
Neo4j Browser → http://localhost:7474
🧪 API Usage
🔹 Endpoint
POST /query
🔹 Request
{
  "question": "What is the temperature in the living room?"
}
🔹 Response
{
  "answer": "The temperature in the living room is 72°F.",
  "reasoning_trace": [
    "Step 1: Parsed user query",
    "Step 2: Generated Cypher query",
    "Step 3: Retrieved data from Neo4j",
    "Step 4: Generated final response"
  ],
  "retrieved_context": "72°F",
  "confidence_score": 0.95
}

🔍 Key Components
🤖 Agent (agent.py)
Tool selection (Cypher vs Semantic)
Multi-step reasoning loop
Guardrails & validation
Response generation
🗄 Database (database.py)
Neo4j connection
Cypher execution
Vector search (semantic retrieval)
Embedding generation
🛠 Tools (tools.py)
execute_cypher
semantic_search
get_device_state
🛡 Hallucination Prevention

The system ensures reliable outputs using:

✅ Grounded retrieval (Neo4j)
✅ Rule-based query validation
✅ No-data fallback handling
✅ Answer verification layer
✅ Controlled prompting
🧪 Testing

Run:

python tests/test_agent.py
📦 Docker Setup
Services
neo4j → Graph database
api → FastAPI application

🔥 Example Queries
What is the temperature in the living room?
Which devices are in the kitchen?
Describe devices in the bedroom
Is any light ON?

🚀 Future Improvements
Multi-turn conversation memory
Advanced tool routing
LangGraph integration (optional)
Real-time device updates
UI dashboard