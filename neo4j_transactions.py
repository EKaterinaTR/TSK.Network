from typing import Iterable

from neo4j import Transaction


def add_user(tx: Transaction, user_id, graph_owner_id: int):
    tx.run('CREATE (u:User {id: $id, graph_owner_id: $graph_owner_id})', id=user_id, graph_owner_id=graph_owner_id)


def add_users(tx: Transaction, user_ids: set[int], graph_owner_id: int):
    tx.run('''
    UNWIND $user_ids AS x
    MERGE (u:User {id: x, graph_owner_id: $graph_owner_id})
    ''', user_ids=list(user_ids), graph_owner_id=graph_owner_id)


def add_user_connection(tx: Transaction, subscriber_from_id: int, subscriber_to_id: int, connection_type: str, graph_owner_id: int):
    if connection_type not in ['FRIEND', 'FOLLOWER']:
        raise ValueError('Attempted to use unsupported connection_type')
    tx.run(f'''
    MATCH (a: User), (b: User)
    WHERE a.id = $subscriber_from_id AND b.id = $subscriber_to_id
      AND a.graph_owner_id = $graph_owner_id AND b.graph_owner_id = $graph_owner_id
    CREATE (a) -[:{connection_type}]-> (b)
    ''', subscriber_from_id=subscriber_from_id, subscriber_to_id=subscriber_to_id, graph_owner_id=graph_owner_id)


def add_friendships(tx: Transaction, user_id: int, friends_ids: list[int], graph_owner_id: int):
    tx.run('''
    MATCH (a: User), (b: User)
    WHERE a.id = $user_id AND b.id IN $friends_ids
      AND a.graph_owner_id = $graph_owner_id AND b.graph_owner_id = $graph_owner_id
    CREATE (a) -[:FRIEND]-> (b)
    ''', user_id=user_id, friends_ids=friends_ids, graph_owner_id=graph_owner_id)


def add_followers(tx: Transaction, followers_ids: list[int], user_id: int, graph_owner_id: int):
    tx.run('''
    MATCH (a: User), (b: User)
    WHERE a.id = $user_id AND b.id IN $followers_ids
      AND a.graph_owner_id = $graph_owner_id AND b.graph_owner_id = $graph_owner_id
    CREATE (a) <-[:FOLLOWER]- (b)
    ''', user_id=user_id, followers_ids=followers_ids, graph_owner_id=graph_owner_id)


def fix_one_directional_friendships(tx: Transaction, graph_owner_id: int):
    tx.run(f'''
    MATCH (a:User) -[:FRIEND]-> (b:User)
    WHERE NOT (a) <-[:FRIEND]- (b)
      AND a.graph_owner_id = $graph_owner_id AND b.graph_owner_id = $graph_owner_id
    CREATE (a) <-[:FRIEND]- (b)
    ''', graph_owner_id=graph_owner_id)


# def get_user(tx: Transaction, user_id):
#     query = '''
#     MATCH (a: User)
#     WHERE a.id = $id
#     RETURN a
#     '''
#     for record in tx.run(query, id=user_id):
#         return record


#def add_friendship(tx: Transaction, user1_id: int, user2_id: int):
#    add_user_subscription(tx, user1_id, user2_id)
#    add_user_subscription(tx, user2_id, user1_id)


def add_user_infos(tx: Transaction, user_infos: Iterable[dict]):
    user_infos = list(user_infos)
    tx.run('''
    UNWIND $user_infos AS row
    MATCH (a: User {id: row.id})
    SET a.name = row.name, a.surname = row.surname
    ''', user_infos=user_infos)


def get_connections(tx: Transaction) -> list[list[int, int, str]]:
    result = tx.run('''
    MATCH (a)-[r]-(b)
    RETURN a.id, b.id, TYPE(r)
    ''')
    return [record.values() for record in result]


def get_nodes(tx: Transaction) -> list[dict]:
    result = tx.run('''
    MATCH (a:User)
    RETURN properties(a)
    ''')
    return [record.values()[0] for record in result]


_algorithm_names_to_function_names = {'page_rank': 'gds.pageRank', 'hits': 'gds.alpha.hits'}
_algorithm_names_to_property_names = {'page_rank': 'page_rank_result', 'hits': 'hits_result_'}

def run_graph_algorithm(tx: Transaction, graph_owner_id: int, algorithm='page_rank', hitsIterations=20):
    # Just in case, to avoid "SQL injections" (the language is not SQL, but anyway)
    if not type(graph_owner_id) == int:
        raise ValueError('graph_owner_id must be int')
    if not type(hitsIterations) == int:
        raise ValueError('hitsIterations must be int')
    if not algorithm in _algorithm_names_to_function_names:
        raise ValueError('Unsupported graph algorithm')
    function_name = _algorithm_names_to_function_names[algorithm]

    graph_name = f'graph_{graph_owner_id}'

    # Creates graph
    tx.run(f"""
    CALL gds.graph.project.cypher(
        '{graph_name}',
        'MATCH (u:User) WHERE u.graph_owner_id = 0 RETURN id(u) AS id',
        'MATCH (a:User)-[r]->(b:User) RETURN id(a) AS source, id(b) AS target'
    )
    """, graph_owner_id=graph_owner_id)

    properties = f"writeProperty: '{_algorithm_names_to_property_names[algorithm]}'"
    if function_name == 'gds.alpha.hits':
        properties += f", hitsIterations: {hitsIterations}"

    # Computes Page Rank and adds it to node properties
    tx.run(f"""
    CALL {function_name}.write('{graph_name}', {{{properties}}})
    """)
    # Deletes graph (nodes and relationships are not removed)
    tx.run(f"""
    CALL gds.graph.drop('{graph_name}')
    """)


def clear_graph_by_owner(tx: Transaction, graph_owner_id: int):
    tx.run('''
    MATCH (n:User {graph_owner_id: $graph_owner_id})
    DETACH DELETE n
    ''', graph_owner_id=graph_owner_id)