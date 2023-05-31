from vk_api import VkApi


def get_user_id(token: str, name_to_resolve: str):
    """
    Returns user id by name. Name is a string after vk url.
    If the name doesn't belong to user, raises ValueError.
    """
    get_id_result = get_id(token, name_to_resolve)
    if get_id_result['type'] != 'user':
        raise ValueError(f'Name "{name_to_resolve}" belongs to {get_id_result["type"]}, not to user')
    return get_id_result['object_id']


def get_group_id(token: str, name_to_resolve: str):
    """
    Returns group id by name. Name is a string after vk url.
    If the name doesn't belong to group, raises ValueError.
    """
    get_id_result = get_id(token, name_to_resolve)
    if get_id_result['type'] != 'group':
        raise ValueError(f'Name "{name_to_resolve}" belongs to {get_id_result["type"]}, not to group')
    return get_id_result['object_id']


def get_id(token: str, name_to_resolve: str) -> dict:
    """
    Returns id by name. Name is a string after vk url.
    :return: Dict with fields: "object_id" (id) and "type" (one of: "user", "group", "event", "page", "application", "vk_app").
    """
    api = get_vk_api(token)
    return api.utils.resolve_screen_name(screen_name=name_to_resolve)



def get_vk_api(token: str):
    vk_session = VkApi(token=token)
    return vk_session.get_api()
