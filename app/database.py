import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


class Neo4jManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def query(self, query: str, params: dict = None):
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            return {"error": str(e)}

    # 🔥 Embedding (NEW MODEL)
    def embed_text(self, text: str):
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return result.embeddings[0].values

    # 🔥 Semantic Search
    def semantic_search(self, query: str, top_k=3):
        embedding = self.embed_text(query)

        cypher = """
        CALL db.index.vector.queryNodes('device_description_embeddings', $top_k, $embedding)
        YIELD node, score
        RETURN node.id AS id, node.type AS type, node.location AS location, node.description AS description, score
        """

        return self.query(cypher, {
            "embedding": embedding,
            "top_k": top_k
        })

    def close(self):
        self.driver.close()