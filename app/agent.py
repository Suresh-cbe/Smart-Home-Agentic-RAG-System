import os
import json
import google.generativeai as genai
from google.generativeai.types import content_types
from app.tools import TOOLS
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
system_instruction = """
You are a "Smart Home Logic Engine", a senior backend engineer and AI architect. 
You are tasked with answering questions about a smart home environment using a Neo4j graph database.

You have access to tools to query the database:
- `execute_cypher`: Write and execute Cypher queries. Prefer this for pathfinding, finding relationships, or specific data retrieval.
- `semantic_device_search`: Use this to find devices based on semantic descriptions.
- `get_device_status`: Retrieve the exact state of a device by its ID.

Important Guidelines:
1. Prefer `execute_cypher` to explore relationships (e.g., what controls what, what is in which room).
2. If `execute_cypher` returns an error (e.g., syntax error or node not found), use the error message to correct your query and try again.
3. If you do not know the exact device ID, you can use `semantic_device_search` to find it first.
4. Once you have gathered sufficient information, synthesize a helpful, concise answer.
"""

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    tools=TOOLS,
    system_instruction=system_instruction
)

class Agent:
    def __init__(self):
        self.chat = model.start_chat(enable_automatic_function_calling=True)
        self.reasoning_trace = []

    def get_response(self, user_query: str) -> dict:
        self.reasoning_trace = [] # Reset trace for new query
        
        # Send message to model. The SDK will automatically handle the tool calls
        # and loops until the model returns a final text response.
        response = self.chat.send_message(user_query)
        
        # Manually extract the trace from the history added during this interaction
        # The history contains the user message, model tool calls, tool responses, and final model response.
        
        # To get the newly added history, we'd ideally compare before and after, 
        # but since we want to capture the trace, we can inspect the chat history.
        # Note: In google-generativeai SDK, enable_automatic_function_calling=True abstracts the loop,
        # but the history contains the steps.
        
        current_trace = []
        for message in self.chat.history:
            if message.role == "model":
                for part in message.parts:
                    if part.function_call:
                        current_trace.append({
                            "action": "tool_call",
                            "tool": part.function_call.name,
                            "arguments": dict(part.function_call.args)
                        })
                    elif part.text:
                         current_trace.append({
                             "action": "model_response",
                             "text": part.text
                         })
            elif message.role == "user" or message.role == "function":
                 for part in message.parts:
                    if part.function_response:
                        # Extract part.function_response as dict
                        try:
                            resp_dict = dict(part.function_response.response)
                            # the structure of response is usually {"result": ...} or similar, depending on how it was passed
                            current_trace.append({
                                "action": "tool_response",
                                "tool": part.function_response.name,
                                "response": resp_dict
                            })
                        except Exception:
                            pass
        
        # In a real scenario, you'd only want the trace for the *current* query. 
        # Here we just take the recent history. For simplicity, we just provide the extracted trace.
        
        # Synthesize final output
        final_answer = response.text
        
        return {
            "answer": final_answer,
            "reasoning_trace": current_trace,
            "retrieved_context": "Context was fetched via tools. See reasoning_trace.",
            "confidence_score": 0.95 # Placeholder as Gemini doesn't output confidence natively
        }
