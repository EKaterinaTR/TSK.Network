from neo4j import Transaction


def add_user(tx: Transaction, user_id, name, surname):
    name = name + ' ' + surname  # Because I can't figure out how to set custom captions. Should be fine, but can be improved
    tx.run('CREATE (u:User {id: $id, name: $name})',
           id=user_id, name=name, surname=surname)


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
