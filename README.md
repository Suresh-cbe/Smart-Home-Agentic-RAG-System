🏠 Smart Home Agentic RAG (Gemini + Neo4j)

Project ID: 20260211-1
Developed by: Suresh Rajendran | Coimbatore, TN

Vanakkam! This is a high-performance Agentic RAG system built to manage and query smart home ecosystems. Instead of just searching for text, this system uses a Neo4j Knowledge Graph to understand how devices actually relate to each other (like which sensor triggers which light) and uses Gemini 1.5 Flash as the "brain" to reason through complex queries.

Built with the Google AI SDK (ADK)—clean, fast, and no unnecessary LangGraph overhead.

🛠 What's Under the Hood?
The Brain: Gemini 1.5 Flash (Handling reasoning and function calling).

The Memory: Neo4j Graph Database (Storing device states and relationships).

The API: FastAPI

Search Style: Hybrid RAG (Vector search for meanings + Cypher queries for relationships).

🚀 Getting Started (The "Mass" Way)
Don't sweat the setup. Follow these steps and you'll be up in 5 minutes.

1. Fire up the Database
I've included a docker-compose.yml. Use it to spin up Neo4j without messing up your local machine.

Bash
docker-compose up -d
2. Setup your Environment
Copy the .env.example to .env and put your keys in.

Note: Get your Gemini API key from Google AI Studio. It's free and fast.

3. Install Dependencies
Bash
pip install -r requirements.txt
4. Seed the Data
Before you ask questions, the "house" needs to be built. Run the seeding script to populate 20+ devices and their connections.

Bash
python seed.py
5. Run the Engine
Bash
uvicorn main:app --reload
📍 Example Queries to Try
Once the server is running at localhost:8000, hit the /query endpoint. Gemini will decide whether to look at the graph or search descriptions.

"What devices are in the bedroom?"

"Which sensors trigger the hallway lights?" (Uses Graph traversal)

"What's the status of the front door lock?" (Direct Tool call)

"What happens when motion is detected in the garage?"

🧠 System Design (How it works)
Natural Language Input: You ask a question in plain English.

Function Calling: Gemini looks at the tools I've provided (execute_cypher, semantic_search).

Reasoning: If you ask "What controls the lights?", Gemini knows it needs to run a Cypher query to find CONTROLS relationships.

Data Synthesis: It takes the raw graph data and explains it to you like a human.

Traceability: Every response comes with a reasoning_trace so you can see exactly how the AI "thought" through the problem.

📝 A Note on the Approach
I chose the Google SDK over LangGraph for this specific implementation to keep the latency low and the code maintainable. In a real-world Coimbatore startup environment, we value speed and reliability. By using native function calling, the agent is less prone to "looping" and more focused on returning accurate device states.

Contact: If you run into any issues, you know where to find me—probably at the office in Ultrafly or grabbing a coffee near RS Puram. ☕