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
    # Logging
    # -----------------------------
    def _log(self, action, data):
        self.reasoning_trace.append({"action": action, **data})

    # -----------------------------
    # Clean Cypher Output
    # -----------------------------
    def _clean_cypher(self, query: str) -> str:
        return query.replace("```", "").replace("cypher", "").strip()

    # -----------------------------
    # Safety Guard
    # -----------------------------
    def _is_safe(self, query: str) -> bool:
        forbidden = ["DELETE", "DROP", "REMOVE", "SET", "CREATE"]
        return not any(f in query.upper() for f in forbidden)

    # -----------------------------
    # Tool Selection
    # -----------------------------
    def _decide_tool(self, query: str) -> str:
        if any(word in query.lower() for word in ["describe", "details", "about"]):
            return "semantic"
        return "cypher"

    # -----------------------------
    # Generate Cypher
    # -----------------------------
    def _generate_cypher(self, query: str) -> str:
        prompt = f"""
Convert user query into Cypher.

Schema:
Device(id, type, location, state, description)

Rules:
- Only return Cypher query
- Do not include ``` or explanations
- Use exact labels and properties

Question:
{query}
"""
        res = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        return self._clean_cypher(res.text)

    # -----------------------------
    # Normalize DB Result
    # -----------------------------
    def _normalize_result(self, result: Any) -> List[Dict]:
        if isinstance(result, dict) and "error" in result:
            return []

        normalized = []

        if isinstance(result, list):
            for r in result:
                if "d" in r:
                    d = r["d"]
                else:
                    d = r

                normalized.append({
                    "type": d.get("type"),
                    "location": d.get("location"),
                    "state": d.get("state"),
                    "description": d.get("description")
                })

        return normalized

    # -----------------------------
    # Build Answer (IMPORTANT FIX)
    # -----------------------------
    def _build_answer(self, query: str, data: List[Dict]) -> str:
        if not data:
            return "No data available."

        # Temperature query
        if "temperature" in query.lower():
            for d in data:
                if d.get("state"):
                    return f"The temperature is {d['state']}."

        # Device listing
        device_types = list(set([d["type"] for d in data if d.get("type")]))

        if device_types:
            return f"The devices are: {', '.join(device_types)}."

        # Fallback
        descriptions = [d["description"] for d in data if d.get("description")]
        if descriptions:
            return descriptions[0]

        return "Data found but unable to summarize."

    # -----------------------------
    # Verification (soft, not strict)
    # -----------------------------
    def _verify(self, answer: str) -> bool:
        return answer not in ["", "No data available.", "Data found but unable to summarize."]

    # -----------------------------
    # MAIN FUNCTION
    # -----------------------------
    def get_response(self, user_query: str) -> Dict[str, Any]:
        self.reasoning_trace = []

        try:
            self._log("user_query", {"text": user_query})

            tool = self._decide_tool(user_query)
            self._log("tool_selected", {"tool": tool})

            result = None
            cypher = None

            # 🔥 Multi-step retry loop
            for attempt in range(2):

                if tool == "cypher":
                    cypher = self._generate_cypher(user_query)
                    self._log("generated_cypher", {"query": cypher})

                    if not self._is_safe(cypher):
                        raise Exception("Unsafe query detected")

                    result = TOOLS["cypher"](db, cypher)

                else:
                    result = TOOLS["semantic"](db, user_query)

                if result:
                    break

            normalized = self._normalize_result(result)
            self._log("db_result", {"result": normalized})

            # 🔥 Build Answer (FIXED CORE ISSUE)
            answer = self._build_answer(user_query, normalized)

            if not self._verify(answer):
                confidence = 0.3
            else:
                confidence = 0.95

            self._log("model_response", {"text": answer})

            return {
                "answer": answer,
                "reasoning_trace": self.reasoning_trace,
                "retrieved_context": normalized,
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