from djproject.neo4j_query import Neo4JQuery

neo4j = Neo4JQuery(graph_owner_id=0)
print(neo4j.get_connections())
print(neo4j.get_nodes())
