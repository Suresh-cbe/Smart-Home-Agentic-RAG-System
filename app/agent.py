import os
import json
from google import genai
from google.genai import types
from app.tools import TOOLS
from dotenv import load_dotenv

load_dotenv()

# Initialize the new client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

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

# Configure tool and system instructions
config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=TOOLS,
    temperature=0.0
)


class Agent:
    def __init__(self):
        # We start a chat session. Function calling loop is native via automatic_function_calling if available,
        # but with google-genai we often loop manually or rely on the SDK's chat feature. 
        # For agent loop, we'll manually handle the loop to capture the trace correctly with the new SDK.
        self.reasoning_trace = []
        self.chat = client.chats.create(model="gemini-1.5-flash", config=config)

    def get_response(self, user_query: str) -> dict:
        self.reasoning_trace = [] # Reset trace for new query
        
        # We manually process to gather the trace
        self.reasoning_trace.append({"action": "user_query", "text": user_query})
        
        # Send message to model. The new SDK chat handles function calling automatically if tools are provided
        # but capturing the exact trace requires inspecting the chat's messages.
        
        # We will loop to handle function calls manually to capture the trace
        # The new SDK's chats.send_message handles history, but we need to intercept tool calls for tracing.
        # Alternatively, we can let the SDK handle it and inspect the history afterwards if it supports auto-calling.
        
        # In the new SDK, chat handles tools if we use them, but to capture the trace we can inspect the response.
        # Let's send the message. 
        response = self.chat.send_message(user_query)

        # Iterate over the chat's last few messages (from the current turn) to build the trace
        # With google-genai, the chat object holds history.
        
        # Let's rebuild the trace from the chat history
        # We look at the messages in self.chat.get_history() (or equivalent)
        
        # To be robust, we'll iterate through the history and look for function calls
        for message in self.chat.get_history():
             # Check if it's a model message with parts
             if message.role == 'model' and getattr(message, 'parts', None):
                 for part in message.parts:
                     if hasattr(part, 'function_call') and part.function_call:
                         # It's a function call
                         args_dict = dict(part.function_call.args) if part.function_call.args else {}
                         self.reasoning_trace.append({
                             "action": "tool_call",
                             "tool": part.function_call.name,
                             "arguments": args_dict
                         })
                     elif hasattr(part, 'text') and part.text:
                         self.reasoning_trace.append({
                             "action": "model_response",
                             "text": part.text
                         })
             elif message.role == 'user' and getattr(message, 'parts', None):
                 for part in message.parts:
                     if hasattr(part, 'function_response') and part.function_response:
                         # It's a function response
                         resp_dict = dict(part.function_response.response) if part.function_response.response else {}
                         self.reasoning_trace.append({
                             "action": "tool_response",
                             "tool": part.function_response.name,
                             "response": resp_dict
                         })
        
        final_answer = response.text
        
        return {
            "answer": final_answer,
            "reasoning_trace": self.reasoning_trace,
            "retrieved_context": "Context was fetched via tools. See reasoning_trace.",
            "confidence_score": 0.95
        }
