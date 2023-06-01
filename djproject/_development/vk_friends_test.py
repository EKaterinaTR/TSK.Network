from vk_friends import FriendsLoader
import test_user_ids


FriendsLoader().run(user_id=test_user_ids.user_id_arthur, depth=1, graph_owner_id=0, followers=False)
