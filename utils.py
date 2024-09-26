import vk_api
from datetime import datetime

from config import *


def create_vk_session(token):
    """
    Создает сессию VK API.
    
    :param token: Токен доступа к API ВКонтакте.
    :return: Объект сессии vk_session.
    """
    return vk_api.VkApi(token=token)


def get_owner_id(vk_session, domain):
    """
    Получает owner_id группы по ее домену.
    
    :param vk_session: Сессия VkApi.
    :param domain: Домен группы (например, "public12345").
    :return: owner_id группы.
    """
    
    vk = vk_session.get_api()
    response = vk.groups.getById(group_id=domain)
    
    if response:
        group_info = response[0]
        owner_id = -group_info['id'] 
        return owner_id
    
    return None


def get_post_ids(vk_session, domain, start_date, end_date):
    """
    Получает все post_id за указанный промежуток времени из паблика по домену.

    :param domain: Домен паблика (например, 'public_name').
    :param start_date: Дата начала периода в формате 'YYYY-MM-DD'.
    :param end_date: Дата конца периода в формате 'YYYY-MM-DD'.
    :param token: Токен доступа к API ВКонтакте.
    :return: Список post_id.
    """
    
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    
    vk = vk_session.get_api()
    
    post_ids = []
    offset = 0
    count = 100
    
    while True:
        response = vk.wall.get(domain=domain, count=count, offset=offset)
        posts = response['items']
        if not posts:
            break
        for post in posts:
            post_date = post['date']
            if post_date > end_timestamp:
                continue
            if post_date < start_timestamp:
                return post_ids
            post_ids.append(post['id'])
        offset += count
    return post_ids