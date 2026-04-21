import os
from google import genai
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def query(self, query: str, parameters=None):
        if parameters is None:
            parameters = {}
        with self.driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record.data() for record in result]
            except Exception as e:
                return {"error": str(e)}

    def get_living_room_temperature(self):
        query = """
        MATCH (d:Device)
        WHERE d.type = 'Thermostat' AND d.location = 'Living Room'
        RETURN d.state AS temperature
        LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            return record["temperature"] if record else None

    def execute_cypher(self, query: str):
        """Execute a Cypher query on the Neo4j database."""
        return self.query(query)

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for text using Gemini text-embedding-004."""
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return result.embeddings[0].values

    def seed_database(self):
        """Seed the Neo4j database with smart home devices and relationships."""
        devices = [
            {"id": "T1", "type": "Thermostat", "location": "Living Room", "state": "72°F", "description": "Smart thermostat controlling the temperature of the main living area."},
            {"id": "T2", "type": "Thermostat", "location": "Master Bedroom", "state": "68°F", "description": "Secondary thermostat for personal comfort in the bedroom."},
            {"id": "L1", "type": "Light", "location": "Living Room", "state": "ON", "description": "Main overhead dimmable LED light in the living room."},
            {"id": "L2", "type": "Light", "location": "Living Room", "state": "OFF", "description": "Floor lamp near the reading chair."},
            {"id": "L3", "type": "Light", "location": "Kitchen", "state": "ON", "description": "Under-cabinet lighting for meal prep."},
            {"id": "L4", "type": "Light", "location": "Kitchen", "state": "ON", "description": "Overhead island pendant lights."},
            {"id": "L5", "type": "Light", "location": "Master Bedroom", "state": "OFF", "description": "Left nightstand reading light."},
            {"id": "L6", "type": "Light", "location": "Master Bedroom", "state": "OFF", "description": "Right nightstand reading light."},
            {"id": "L7", "type": "Light", "location": "Bathroom", "state": "OFF", "description": "Vanity mirror lights."},
            {"id": "S1", "type": "Sensor", "location": "Front Door", "state": "CLOSED", "description": "Contact sensor for the main entry door."},
            {"id": "S2", "type": "Sensor", "location": "Back Door", "state": "LOCKED", "description": "Smart lock and contact sensor for the patio door."},
            {"id": "S3", "type": "Sensor", "location": "Living Room", "state": "NO_MOTION", "description": "Motion and ambient light sensor in the living room."},
            {"id": "S4", "type": "Sensor", "location": "Hallway", "state": "NO_MOTION", "description": "Motion sensor to trigger path lighting."},
            {"id": "S5", "type": "Sensor", "location": "Kitchen", "state": "MOTION_DETECTED", "description": "Motion sensor for automated kitchen lights."},
            {"id": "S6", "type": "Sensor", "location": "Master Bedroom", "state": "NO_MOTION", "description": "Occupancy sensor to determine if someone is in bed."},
            {"id": "C1", "type": "Camera", "location": "Front Porch", "state": "RECORDING", "description": "Security camera covering the driveway and front door."},
            {"id": "C2", "type": "Camera", "location": "Backyard", "state": "IDLE", "description": "Security camera monitoring the patio and yard."},
            {"id": "SP1", "type": "SmartPlug", "location": "Living Room", "state": "ON", "description": "Smart plug controlling the TV entertainment center."},
            {"id": "SP2", "type": "SmartPlug", "location": "Bedroom", "state": "OFF", "description": "Smart plug connected to a space heater."},
            {"id": "A1", "type": "Appliance", "location": "Kitchen", "state": "RUNNING", "description": "Smart refrigerator with energy monitoring."},
            {"id": "A2", "type": "Appliance", "location": "Laundry Room", "state": "IDLE", "description": "Smart washing machine."}
        ]

        relationships = [
            ("L1", "IN_ROOM", "Living Room"),
            ("L2", "IN_ROOM", "Living Room"),
            ("T1", "CONTROLS_TEMP_IN", "Living Room"),
            ("S3", "MONITORS_MOTION_IN", "Living Room"),
            ("SP1", "POWERS", "Entertainment Center"),
            ("L3", "IN_ROOM", "Kitchen"),
            ("L4", "IN_ROOM", "Kitchen"),
            ("S5", "MONITORS_MOTION_IN", "Kitchen"),
            ("A1", "LOCATED_IN", "Kitchen"),
            ("L5", "IN_ROOM", "Master Bedroom"),
            ("L6", "IN_ROOM", "Master Bedroom"),
            ("T2", "CONTROLS_TEMP_IN", "Master Bedroom"),
            ("S6", "MONITORS_OCCUPANCY_IN", "Master Bedroom"),
            ("S1", "SECURES", "Front Door"),
            ("C1", "WATCHES", "Front Door"),
            ("S2", "SECURES", "Back Door"),
            ("C2", "WATCHES", "Backyard"),
            ("S4", "MONITORS_MOTION_IN", "Hallway"),
            ("L7", "IN_ROOM", "Bathroom"),
            ("SP2", "LOCATED_IN", "Master Bedroom"),
            ("A2", "LOCATED_IN", "Laundry Room"),
            ("S3", "TRIGGERS", "L1"),
            ("S5", "TRIGGERS", "L3"),
            ("S4", "TRIGGERS", "L2"),
            ("S1", "ALERTS", "C1")
        ]

        # Clear existing data
        self.query("MATCH (n) DETACH DELETE n")

        # Create nodes and generate embeddings
        for d in devices:
            embedding = self.embed_text(d["description"])
            self.query(
                """
                CREATE (n:Device {
                    id: $id, 
                    type: $type, 
                    location: $location, 
                    state: $state, 
                    description: $description,
                    embedding: $embedding
                })
                """,
                {
                    "id": d["id"],
                    "type": d["type"],
                    "location": d["location"],
                    "state": d["state"],
                    "description": d["description"],
                    "embedding": embedding
                }
            )

        # Create relationships
        for source, rel_type, target in relationships:
            # We treat target as a Room/Area node if it doesn't exist as a device
            self.query(
                f"""
                MERGE (t:Location {{name: $target}})
                WITH t
                MATCH (s:Device {{id: $source}})
                MERGE (s)-[:{rel_type}]->(t)
                """,
                {"source": source, "target": target}
            )

        # Create vector index
        try:
            self.query("""
            CREATE VECTOR INDEX device_description_embeddings IF NOT EXISTS
            FOR (d:Device) ON (d.embedding)
            OPTIONS {indexConfig: {
             `vector.dimensions`: 768,
             `vector.similarity_function`: 'cosine'
            }}
            """)
        except Exception as e:
            print(f"Index creation error or already exists: {e}")

        print("Database seeded successfully.")

if __name__ == "__main__":
    db = Neo4jManager()
    db.seed_database()
    db.close()
