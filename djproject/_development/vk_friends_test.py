from _development import test_constants
from _development.test_constants import VK_API_KEY
from djproject.vk_friends import FriendsLoader


FriendsLoader().run(token=VK_API_KEY, user_id=test_constants.user_id_arthur, depth=1, graph_owner_id=0, followers=False)
