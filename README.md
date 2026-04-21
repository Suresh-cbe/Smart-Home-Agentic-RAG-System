🏠 Smart Home Agentic RAG System

An intelligent Agentic Retrieval-Augmented Generation (RAG) system for smart home environments, powered by FastAPI, Neo4j, and LLMs.
This system enables natural language interaction with smart devices using structured graph data and semantic retrieval.

🚀 Features
🔍 Hybrid Retrieval
Graph-based queries using Neo4j (Cypher)
Semantic search using embeddings
🧠 Agentic Reasoning
Multi-step reasoning pipeline
Tool selection (Cypher vs Semantic)
🛡️ Reliability & Guardrails
Query validation layer
No-data fallback handling
Answer verification
Hallucination prevention
⚡ FastAPI Backend
High-performance API endpoints
Scalable architecture
📦 Installation
1. Clone Repository
git clone <your-repo-url>
cd smart-home-agentic-rag
2. Create Environment File

Create a .env file in the root directory:

GOOGLE_API_KEY=your_api_key
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

⚠️ Important: Never commit .env to GitHub. Use .env.example instead.

3. Install Dependencies
pip install -r requirements.txt
4. Run with Docker
docker-compose up --build
🌐 Services
FastAPI Docs: http://localhost:8000/docs
Neo4j Browser: http://localhost:7474
📡 API Usage
Endpoint
POST /query
Request
{
  "question": "What is the temperature in the living room?"
}
Response
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
🧩 Project Structure
app/
├── agent.py        # Agent logic & reasoning
├── database.py     # Neo4j connection & queries
├── tools.py        # Tool implementations
├── main.py         # FastAPI entry point
🔑 Key Components
Agent (agent.py)
Tool selection logic
Multi-step reasoning loop
Database (database.py)
Neo4j connection
Cypher query execution
Tools (tools.py)
execute_cypher
semantic_search
get_device_state
✅ Reliability Mechanisms
✔️ Grounded retrieval (Neo4j)
✔️ Rule-based query validation
✔️ No-data fallback handling
✔️ Answer verification layer
✔️ Controlled prompting
✔️ Testing support
🧪 Run Tests
python tests/test_agent.py
💡 Example Queries
What is the temperature in the living room?
Which devices are in the kitchen?
Describe devices in the bedroom
Is any light ON?
🔮 Future Improvements
🔁 Multi-turn conversation memory
⚙️ Advanced tool routing
🔗 LangGraph integration (optional)
📡 Real-time device updates
📊 UI dashboard
⚠️ Security Best Practices
Never expose .env file publicly
Rotate API keys if exposed
Use environment variables in production
Prefer secret managers (Docker / Cloud)
