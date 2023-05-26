from functools import partial
from multiprocessing.pool import ThreadPool

import vk_api.exceptions
from neo4j import GraphDatabase, Session, Driver
from vk_api import VkApi
from vk_api.vk_api import VkApiMethod
from py_linq import Enumerable

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

        self._add_user_infos()

        self._driver.close()


    def _run_step(self, last_step=False):
        handle_user_partial = partial(self._handle_user, last_step=last_step)
        with ThreadPool() as pool:
            pool.map(handle_user_partial, self._current_step_users)
        #list(map(self._handle_user, self._current_step_users))


    def _handle_user(self, user_id: int, last_step=False):
        #try:
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            friend_ids = set(self._vk_get_friends(user_id))
            follower_ids = set(self._vk_get_followers(user_id))
            if last_step:
                friend_ids &= self._created_users
                follower_ids &= self._created_users
            else:
                # TODO maybe some ids can be excluded here?
                ids = friend_ids | follower_ids
                self._next_step_candidates |= ids

                users_to_add = ids - self._created_users
                self._add_users(session, users_to_add)

            session.execute_write(neo4j_transactions.add_friendships, user_id, list(friend_ids))
            if self._followers:
                session.execute_write(neo4j_transactions.add_followers, list(follower_ids), user_id)


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
        session.execute_write(neo4j_transactions.add_user, user_id)
        self._created_users.add(user_id)


    def _add_users(self, session: Session, user_ids: set[int]):
        session.execute_write(neo4j_transactions.add_users, user_ids)
        self._created_users |= user_ids

    def _add_user_infos(self):
        # TODO check if it works with many users
        # Maybe if user count is high, user list should be split to batches and distributed between threads?
        user_infos = Enumerable(self._vk.users.get(user_ids=list(self._created_users), lang='ru')).select(preprocess_user_info)
        with self._driver.session(database=constants.NEO4J_DATABASE_NAME) as session:
            session.execute_write(neo4j_transactions.add_user_infos, user_infos=user_infos)


def range_closed(start, stop, step=1):
    """
    Returns closed range, which includes borders. Made to improve code readability, as half-open range can be confusing
    in cases like when step is negative.

    Equivalent to range(start, stop + step, step)
    """
    return range(start, stop + step, step)


def preprocess_user_info(user_info: dict):
    return {
        'id': user_info['id'],
        'name': user_info['first_name'],
        'surname': user_info['last_name']
    }
