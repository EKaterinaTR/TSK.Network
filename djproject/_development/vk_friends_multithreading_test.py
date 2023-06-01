from time import time
from _development import test_constants
from _development.test_constants import VK_API_KEY
from djproject.vk_friends import FriendsLoader


print('With multithreading:')
start_time = time()
FriendsLoader().run(token=VK_API_KEY, user_id=test_constants.user_id_arthur, depth=1, graph_owner_id=10, followers=False)
print(time() - start_time)

print('Without multithreading:')
start_time = time()
FriendsLoader(multithreading=False).run(token=VK_API_KEY, user_id=test_constants.user_id_arthur, depth=1, graph_owner_id=10, followers=False)
print(time() - start_time)
