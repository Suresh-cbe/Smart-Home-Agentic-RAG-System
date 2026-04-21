def execute_cypher(db, query):
    return db.query(query)
def semantic_search_tool(db, query):
    return db.semantic_search(query)
def get_device_state(db, device_id):
    return db.query(
        "MATCH (d:Device {id: $id}) RETURN d.state",
        {"id": device_id}
    )