from _development import test_constants
from djproject.vk_friends import FriendsLoader


FriendsLoader().run(user_id=test_constants.user_id_arthur, depth=1, graph_owner_id=0, followers=False)
