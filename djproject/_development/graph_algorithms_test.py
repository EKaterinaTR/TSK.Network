from djproject.neo4j_query import Neo4JQuery

neo4j = Neo4JQuery(graph_owner_id=0)
neo4j.page_rank()
neo4j.hits()
print(neo4j.get_nodes())
