from time import time

import requests
import vk_api

from _development.test_constants import VK_API_KEY, user_id_artem
from djproject.vk_utils import get_vk_api


iterations_count = 10


print('vk-api:')
api = get_vk_api(VK_API_KEY)
start_time = time()
for i in range(iterations_count):
    _ = api.friends.get(user_id=user_id_artem)
print((time() - start_time) / iterations_count)


print('requests:')
api = get_vk_api(VK_API_KEY)
start_time = time()
for i in range(iterations_count):
    _ = requests.get('https://api.vk.com/method/friends.get?' +
                     f'user_id={user_id_artem}&' +
                     'v=5.131&' +
                     'access_token=' + VK_API_KEY).json()['response']
print((time() - start_time) / iterations_count)
