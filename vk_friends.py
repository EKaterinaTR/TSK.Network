from functools import partial
#from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
import traceback

import vk_api.exceptions
from neo4j import GraphDatabase, Transaction, Session, Driver
from vk_api import VkApi

from constants import VK_API_KEY


class FriendsLoader:
    def __init__(self):
        self._users_of_previous_steps: set | None = None
        self._current_step_users: set | None = None
        self._next_step_candidates: set | None = None
        self._created_users: set | None = None
        # TODO actually use data from this set
        self._private_profiles: set | None = None
        self._driver: Driver | None = None

        vk_session = VkApi(token=VK_API_KEY)
        self._vk = vk_session.get_api()


    def run(self, user_id: int, recursion_depth: int):
        self._users_of_previous_steps = set()
        self._current_step_users = set()
        self._next_step_candidates = set()
        self._created_users = set()
        self._private_profiles = set()

        self._driver = GraphDatabase.driver('neo4j+s://69c255a0.databases.neo4j.io', auth=('neo4j', 'E1Y7GU9nTNvIaNQKZRN-MXeJHkB-W_-xliZoy-ubseo'), max_connection_lifetime=120)

        with self._driver.session(database="neo4j") as session:
            self.add_user(session, user_id)

        self._current_step_users.add(user_id)

        for step_number in range_closed(recursion_depth, 1, -1):
            self._run_step()
            self._users_of_previous_steps |= self._current_step_users
            self._current_step_users = self._next_step_candidates - self._users_of_previous_steps
        self._run_step(last_step=True)

        self._driver.close()


    def _run_step(self, last_step=False):
        handle_user_partial = partial(self._handle_user, last_step=last_step)
        with ThreadPool() as pool:
            pool.map(handle_user_partial, self._current_step_users)
        #list(map(self._handle_user, self._current_step_users))


    def _handle_user(self, user_id: int, last_step=False):
        #try:
        with self._driver.session(database="neo4j") as session:
            friend_ids = self.vk_get_friends(user_id)
            for friend_id in friend_ids:
                if friend_id not in self._created_users:
                    if not last_step:
                        self.add_user(session, friend_id)
                    else:
                        continue
                session.execute_write(add_user_connection, user_id, friend_id)
                self._next_step_candidates.add(friend_id)
        #except Exception as e:
        #    traceback.print_exc()
        #    raise e



    def vk_get_friends(self, user_id) -> list:
        try:
            return self._vk.friends.get(user_id=user_id)['items']
        except vk_api.exceptions.ApiError as e:
            if str(e) == '[30] This profile is private':
                self._private_profiles.add(user_id)
                return []
            raise e





    def add_user(self, session: Session, user_id: int):
        self._created_users.add(user_id)
        user = self._vk.users.get(user_id=user_id)[0]
        session.execute_write(add_user, user_id, user['first_name'], user['last_name'])



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


def add_user_connection(tx: Transaction, subscriber_from_id: int, subscriber_to_id: int):
    tx.run('''
    MATCH (a: User), (b: User)
    WHERE a.id = $subscriber_from_id AND b.id = $subscriber_to_id
    CREATE (a) -[:USER_TO_USER]-> (b)
    ''', subscriber_from_id=subscriber_from_id, subscriber_to_id=subscriber_to_id)


#def add_friendship(tx: Transaction, user1_id: int, user2_id: int):
#    add_user_subscription(tx, user1_id, user2_id)
#    add_user_subscription(tx, user2_id, user1_id)

#TODO
#CREATE CONSTRAINT FOR (user:User) REQUIRE user.id IS UNIQUE

def range_closed(a, b, step=1):
    return range(a, b + step, step)


if __name__ == '__main__':
    #user_id = 117547723
    user_id = 259182295
    FriendsLoader().run(user_id=user_id, recursion_depth=1)