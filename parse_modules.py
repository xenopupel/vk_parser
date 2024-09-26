import json

from config import *


def get_post_info(vk_session, owner_id, post_id):
    """
    Получает текст поста и его характеристики.
    
    :param vk_session: Сессия VkApi.
    :param owner_id: Идентификатор владельца поста.
    :param post_id: Идентификатор поста.
    :return: Словарь с информацией о посте.
    """
    
    vk = vk_session.get_api()
    response = vk.wall.getById(posts=f"{owner_id}_{post_id}")
    
    if response:
        post = response[0]
        post_info = {
            'post_id': post_id,
            'owner_id': owner_id,
            'text': post['text'],
            'likes': post['likes']['count'],
            'views': post['views']['count'],
            'reposts': post['reposts']['count'],
            'date': post['date']
        }
        return post_info
    
    return None


def get_comments(vk_session, owner_id, post_id):
    """
    Получает все комментарии к посту, включая комментарии к комментариям.
    
    :param vk_session: Сессия VkApi.
    :param owner_id: Идентификатор владельца поста.
    :param post_id: Идентификатор поста.
    :return: Список комментариев к посту.
    """
    
    vk = vk_session.get_api()
    comments_info = []
    
    # Получаем комментарии к посту
    response = vk.wall.getComments(owner_id=owner_id, post_id=post_id, need_likes=1, count=100)
    comments = response['items']
    
    for comment in comments:
        if comment['text'] == '':
            continue

        comment_info = {
            'comment_id': comment['id'],
            'text': comment['text'],
            'likes': comment['likes']['count'],
            'date': comment['date'],
            'replies': get_replies(vk_session, owner_id, post_id, comment['id'])  # Получаем ответы на комментарий
        }
        comments_info.append(comment_info)
    
    return comments_info


def get_replies(vk_session, owner_id, post_id, comment_id):
    """
    Получает все ответы на комментарий.
    
    :param vk_session: Сессия VkApi.
    :param owner_id: Идентификатор владельца поста.
    :param post_id: Идентификатор поста.
    :param comment_id: Идентификатор комментария.
    :return: Список ответов на комментарий.
    """
    
    vk = vk_session.get_api()
    replies_info = []
    
    # Получаем ответы на комментарий
    response = vk.wall.getComments(owner_id=owner_id, post_id=post_id, comment_id=comment_id, need_likes=1, count=100)
    replies = response['items']
    
    for reply in replies:
        if reply['text'] == '':
            continue

        reply_info = {
            'reply_id': reply['id'],
            'text': reply['text'],
            'likes': reply['likes']['count'],
            'date': reply['date']
        }
        replies_info.append(reply_info)
    
    return replies_info


def get_post_data(vk_session, owner_id, post_id):
    """
    Получает информацию о посте и его комментариях в формате JSON.
    
    :param vk_session: Сессия VkApi.
    :param owner_id: Идентификатор владельца поста.
    :param post_id: Идентификатор поста.
    :return: Строка JSON с информацией о посте и комментариях.
    """
    
    post_info = get_post_info(vk_session, owner_id, post_id)
    
    if post_info:
        post_info['comments'] = get_comments(vk_session, owner_id, post_id)
        return json.dumps(post_info, ensure_ascii=False)  # Возвращаем в формате JSON с поддержкой кириллицы
    
    return None


