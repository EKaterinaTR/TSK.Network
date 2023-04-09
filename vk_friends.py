from neo4j import GraphDatabase, Transaction, Session
from vk_api import VkApi

from constants import VK_API_KEY


class FriendsLoader:
    def __init__(self):
        self._visited_ids = None
        self._session: Session | None = None

        vk_session = VkApi(token=VK_API_KEY)
        self._vk = vk_session.get_api()


    def run(self, user_id: int, recursion_depth: int):
        self._visited_ids = set()
        driver = GraphDatabase.driver('neo4j+s://69c255a0.databases.neo4j.io', auth=('neo4j', 'E1Y7GU9nTNvIaNQKZRN-MXeJHkB-W_-xliZoy-ubseo'))
        with driver.session(database='neo4j') as session:
            self._session = session
            self.add_user(user_id)
            self._load_friends_recursive(user_id, recursion_depth)
            self._session = None
        driver.close()


    def _load_friends_recursive(self, user_id: int, recursion_depth: int):
        if recursion_depth == 0:
            return

        friend_ids = self._vk.friends.get(user_id=user_id)['items']
        for friend_id in friend_ids:
            if friend_id not in self._visited_ids:
                self.add_user(friend_id)
                self._session.execute_write(add_friendship, user_id, friend_id)
                self._load_friends_recursive(friend_id, recursion_depth - 1)







    def add_user(self, user_id: int):
        #user = self._session.execute_read(get_user, user_id=user_id)
        user = self._vk.users.get(user_id=user_id)[0]
        self._session.execute_write(add_user, user_id, user['first_name'], user['last_name'])



def add_user(tx: Transaction, user_id, name, surname):
    tx.run('CREATE (u:User {id: $id, name: $name, surname: $surname})',
           id=user_id, name=name, surname=surname)


# def get_user(tx: Transaction, user_id):
#     query = '''
#     MATCH (a: User)
#     WHERE a.id = $id
#     RETURN a
#     '''
#     for record in tx.run(query, id=user_id):
#         return record


def add_user_subscription(tx: Transaction, subscriber_from_id: int, subscriber_to_id: int):
    tx.run('''
    MATCH (a: User), (b: User)
    WHERE a.id = $subscriber_from_id AND b.id = $subscriber_to_id
    CREATE (a) -[:USER_TO_USER]-> (b)
    ''', subscriber_from_id=subscriber_from_id, subscriber_to_id=subscriber_to_id)


def add_friendship(tx: Transaction, user1_id: int, user2_id: int):
    add_user_subscription(tx, user1_id, user2_id)
    add_user_subscription(tx, user2_id, user1_id)


#if __name__ == '__main__':
#    FriendsLoader().run(user_id=259182295, recursion_depth=1)