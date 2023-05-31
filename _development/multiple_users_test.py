from neo4j_query import Neo4JQuery
from vk_friends import FriendsLoader
import test_user_ids


FriendsLoader().run(user_id=test_user_ids.user_id_arthur, depth=1, graph_owner_id=0, followers=False)
FriendsLoader().run(user_id=test_user_ids.user_id_arthur, depth=1, graph_owner_id=1, followers=False)
FriendsLoader().run(user_id=test_user_ids.user_id_arthur, depth=1, graph_owner_id=2, followers=False)

neo4j_0 = Neo4JQuery(graph_owner_id=0)
neo4j_0.page_rank()
x = neo4j_0.get_nodes()
print(x)
print(len(x))
y = neo4j_0.get_connections()
print(y)
print(len(y))
