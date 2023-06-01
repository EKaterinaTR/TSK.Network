from _development.test_constants import VK_API_KEY
from djproject import vk_utils

print(vk_utils.get_id(VK_API_KEY, 'armgnv'))
print(vk_utils.get_user_id(VK_API_KEY, 'armgnv'))
