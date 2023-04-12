from functools import partial
from multiprocessing.pool import ThreadPool

import vk_api.exceptions
from neo4j import GraphDatabase, Session, Driver
from vk_api import VkApi
from vk_api.vk_api import VkApiMethod

import constants
import neo4j_transactions


class FriendsLoader:
    def __init__(self):
        self._users_of_previous_steps: set | None = None
        self._current_step_users: set | None = None
        self._next_step_candidates: set | None = None
        self._created_users: set | None = None

        self._driver: Driver | None = None
        self._vk = VkApiMethod | None
        self._followers: bool | None = None


    def run(self, user_id: int, depth: int, followers=False):
        self._followers = followers
        self._users_of_previous_steps = set()
        self._current_step_users = set()
        self._next_step_candidates = set()
        self._created_users = set()

        vk_session = VkApi(token=constants.VK_API_KEY)
        self._vk = vk_session.get_api()

        self._driver = GraphDatabase.driver(**constants.NEO4J_CONNECTION_PARAMETERS)

        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            self._add_user(session, user_id)

        self._current_step_users.add(user_id)

        for _ in range_closed(depth, 1, -1):
            self._run_step()
            self._users_of_previous_steps |= self._current_step_users
            self._current_step_users = self._next_step_candidates - self._users_of_previous_steps
        self._run_step(last_step=True)

        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            session.execute_write(neo4j_transactions.fix_one_directional_friendships)

        self._driver.close()


    def _run_step(self, last_step=False):
        handle_user_partial = partial(self._handle_user, last_step=last_step)
        with ThreadPool() as pool:
            pool.map(handle_user_partial, self._current_step_users)
        #list(map(self._handle_user, self._current_step_users))


    def _handle_user(self, user_id: int, last_step=False):
        #try:
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            friend_ids = self._vk_get_friends(user_id)
            follower_ids = self._vk_get_followers(user_id)
            for i, friend_id in enumerate(friend_ids + follower_ids):
                if friend_id not in self._created_users:
                    if not last_step:
                        self._add_user(session, friend_id)
                    else:
                        continue
                if i < len(friend_ids):
                    # Friend
                    session.execute_write(neo4j_transactions.add_user_connection, user_id, friend_id, 'FRIEND')
                else:
                    # Follower
                    session.execute_write(neo4j_transactions.add_user_connection, friend_id, user_id, 'FOLLOWER')
                self._next_step_candidates.add(friend_id)

        #except Exception as e:
        #    traceback.print_exc()
        #    raise e


    def _vk_get_friends(self, user_id) -> list:
        try:
            return self._vk.friends.get(user_id=user_id)['items']
        except vk_api.exceptions.ApiError as e:
            if str(e) == '[30] This profile is private':
                return []
            raise e


    def _vk_get_followers(self, user_id) -> list:
        if not self._followers:
            return []
        try:
            return self._vk.users.get_followers(user_id=user_id)['items']
        except vk_api.exceptions.ApiError as e:
            if str(e) == '[30] This profile is private':
                return []
            raise e


    # def _vk_get_user_subscriptions(self, user_id) -> list:
    #     try:
    #         return self._vk.users.get_subscriptions(user_id=user_id)['users']['items']
    #     except vk_api.exceptions.ApiError as e:
    #         if str(e) == '[30] This profile is private':
    #             return []
    #         raise e


    def _add_user(self, session: Session, user_id: int):
        self._created_users.add(user_id)
        user = self._vk.users.get(user_id=user_id, lang='ru')[0]
        session.execute_write(neo4j_transactions.add_user, user_id, user['first_name'], user['last_name'])


def range_closed(start, stop, step=1):
    """
    Returns closed range, which includes borders. Made to improve code readability, as half-open range can be confusing
    in cases like when step is negative.

    Equivalent to range(start, stop + step, step)
    """
    return range(start, stop + step, step)
