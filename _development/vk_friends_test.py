from vk_friends import FriendsLoader
import test_user_ids


FriendsLoader().run(user_id=test_user_ids.user_id_artem, depth=1, followers=True)
