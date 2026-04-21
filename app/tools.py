import json
from app.database import Neo4jManager

# Initialize a global instance or handle it per request
db = Neo4jManager()

def execute_cypher(query: str) -> str:
    """Executes a Cypher query on the Neo4j database to retrieve relationship logic or specific device nodes.
    
    Args:
        query: A valid Neo4j Cypher query string.
    
    Returns:
        A JSON string representation of the query results, or an error message if the query fails.
    """
    result = db.execute_cypher(query)
    return json.dumps(result)

def semantic_device_search(search_query: str) -> str:
    """Uses Neo4j vector search to find devices based on a semantic description.
    
    Args:
        search_query: A natural language description of the device you are looking for.
        
    Returns:
        A JSON string containing the top matching devices, their properties, and similarity scores.
    """
    try:
        query_embedding = db.embed_text(search_query)
        cypher = """
        CALL db.index.vector.queryNodes('device_description_embeddings', 3, $embedding)
        YIELD node, score
        RETURN node.id AS id, node.type AS type, node.location AS location, node.state AS state, node.description AS description, score
        """
        results = db.query(cypher, {"embedding": query_embedding})
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_device_status(device_id: str) -> str:
    """Returns specific status (e.g., '72°F', 'ON') for a given device ID.
    
    Args:
        device_id: The unique identifier of the device (e.g., 'T1', 'L2').
        
    Returns:
        A JSON string containing the device's current state, or an error if not found.
    """
    query = "MATCH (d:Device {id: $device_id}) RETURN d.state AS state"
    result = db.query(query, {"device_id": device_id})
    if result and "state" in result[0]:
        return json.dumps({"status": result[0]["state"]})
    return json.dumps({"error": "Device not found."})

# List of tools to pass to Gemini
TOOLS = [execute_cypher, semantic_device_search, get_device_status]
