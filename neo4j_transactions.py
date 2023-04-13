from typing import Iterable

from neo4j import Transaction


def add_user(tx: Transaction, user_id):
    tx.run('CREATE (u:User {id: $id})', id=user_id)


def add_users(tx: Transaction, user_ids: set[int]):
    tx.run('''
    UNWIND $user_ids AS x
    MERGE (u:User {id: x})
    ''', user_ids=list(user_ids))


def add_user_connection(tx: Transaction, subscriber_from_id: int, subscriber_to_id: int, connection_type: str):
    if connection_type not in ['FRIEND', 'FOLLOWER']:
        raise ValueError('Attempted to use unsupported connection_type')
    tx.run(f'''
    MATCH (a: User), (b: User)
    WHERE a.id = $subscriber_from_id AND b.id = $subscriber_to_id
    CREATE (a) -[:{connection_type}]-> (b)
    ''', subscriber_from_id=subscriber_from_id, subscriber_to_id=subscriber_to_id)


def add_friendships(tx: Transaction, user_id: int, friends_ids: list[int]):
    tx.run('''
    MATCH (a: User), (b: User)
    WHERE a.id = $user_id AND b.id IN $friends_ids
    CREATE (a) -[:FRIEND]-> (b)
    ''', user_id=user_id, friends_ids=friends_ids)


def add_followers(tx: Transaction, followers_ids: list[int], user_id: int):
    tx.run('''
    MATCH (a: User), (b: User)
    WHERE a.id = $user_id AND b.id IN $followers_ids
    CREATE (a) <-[:FOLLOWER]- (b)
    ''', user_id=user_id, followers_ids=followers_ids)


def fix_one_directional_friendships(tx: Transaction):
    tx.run(f'''
    MATCH (a:User) -[:FRIEND]-> (b:User)
    WHERE NOT (a) <-[:FRIEND]- (b)
    CREATE (a) <-[:FRIEND]- (b)
    ''')


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
    SET a.name = row.name
    ''', user_infos=user_infos)
