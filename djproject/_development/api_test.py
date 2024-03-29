import vk_api.exceptions
from vk_api import VkApi

from _development.test_constants import VK_API_KEY


def subscribers_test():
    vk_session = VkApi(token=VK_API_KEY)
    #vk_session.auth()
    vk = vk_session.get_api()
    #print(vk.users.get_followers(user_id=259182295))
    print('getSubscriptions:')
    print(vk.users.get_subscriptions(user_id=117547723))
    print('getFollowers:')
    print(vk.users.get_followers(user_id=117547723))
    #print(vk.friends.get(user_id=117547723))

    #friends_query = vk.friends.get(user_id=259182295)
    #print(type(friends_query))


def get_many_users_test():
    vk_session = VkApi(token=VK_API_KEY)
    vk = vk_session.get_api()
    print(vk.users.get(user_ids=[117547723, 259182295]))


def closed_profile_test():
    vk_session = VkApi(token=VK_API_KEY)
    vk = vk_session.get_api()
    try:
        print(vk.friends.get(user_id=196908431))
    except vk_api.exceptions.ApiError as e:
        print(str(e))


get_many_users_test()
#closed_profile_test()