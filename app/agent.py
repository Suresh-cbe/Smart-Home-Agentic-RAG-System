import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai
from app.database import Neo4jManager
from app.tools import execute_cypher, semantic_search_tool

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
db = Neo4jManager()

TOOLS = {
    "cypher": execute_cypher,
    "semantic": semantic_search_tool
}


class Agent:
    def __init__(self):
        self.reasoning_trace: List[Dict[str, Any]] = []

    # -----------------------------
    # Utilities
    # -----------------------------
    def _log(self, action, data):
        self.reasoning_trace.append({"action": action, **data})

    def _clean_cypher(self, query):
        return query.replace("```", "").replace("cypher", "").strip()

    def _is_safe(self, query):
        forbidden = ["DELETE", "DROP", "REMOVE", "SET", "CREATE"]
        return not any(f in query.upper() for f in forbidden)

    def _format_result(self, result):
        if isinstance(result, list) and result:
            return ", ".join(str(v) for v in result[0].values())
        return "No data available"

    def _verify(self, answer, context):
        return context.lower() in answer.lower()

    # -----------------------------
    # Tool Decision
    # -----------------------------
    def _decide_tool(self, query):
        if any(x in query.lower() for x in ["describe", "about", "details"]):
            return "semantic"
        return "cypher"

    # -----------------------------
    # Generate Cypher
    # -----------------------------
    def _generate_cypher(self, query):
        prompt = f"""
Convert to Cypher.

Schema:
Device(type, location, state)

Rules:
- type: Thermostat | Light | Sensor
- location: Living Room | Kitchen | Bedroom
- Only return Cypher

Question:
{query}
"""
        res = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return self._clean_cypher(res.text)

    # -----------------------------
    # Main Flow
    # -----------------------------
    def get_response(self, user_query: str) -> Dict[str, Any]:
        self.reasoning_trace = []

        try:
            self._log("user_query", {"text": user_query})

            tool = self._decide_tool(user_query)
            self._log("tool_selected", {"tool": tool})

            # 🔥 Multi-step retry loop
            result = None
            cypher = None

            for _ in range(2):
                if tool == "cypher":
                    cypher = self._generate_cypher(user_query)
                    self._log("generated_cypher", {"query": cypher})

                    if not self._is_safe(cypher):
                        raise Exception("Unsafe query")

                    result = TOOLS["cypher"](db, cypher)

                else:
                    result = TOOLS["semantic"](db, user_query)

                if result:
                    break

            context = self._format_result(result)
            self._log("db_result", {"result": context})

            # 🔥 No hallucination guard
            if context == "No data available":
                return {
                    "answer": "No data available.",
                    "reasoning_trace": self.reasoning_trace,
                    "retrieved_context": context,
                    "confidence_score": 0.2
                }

            # 🔥 Final Answer
            prompt = f"""
Answer using ONLY data.

Question:
{user_query}

Data:
{context}
"""
            res = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            answer = res.text.strip()

            if not self._verify(answer, context):
                answer = "Unable to verify answer."
                confidence = 0.3
            else:
                confidence = 0.95

            self._log("model_response", {"text": answer})

            return {
                "answer": answer,
                "reasoning_trace": self.reasoning_trace,
                "retrieved_context": context,
                "confidence_score": confidence
            }

        except Exception as e:
            self._log("error", {"message": str(e)})
            return {
                "answer": "Request failed safely.",
                "reasoning_trace": self.reasoning_trace,
                "retrieved_context": "",
                "confidence_score": 0.0
            }