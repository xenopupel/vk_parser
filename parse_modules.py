import json
import datetime

from tqdm import tqdm
from config import *
from utils import get_owner_id, get_post_ids


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
        date_str = datetime.datetime.fromtimestamp(post["date"]).strftime("%d-%m-%Y")
        post_info = {
            "post_id": post_id,
            "owner_id": owner_id,
            "text": post["text"],
            "likes": post["likes"]["count"],
            "views": post["views"]["count"],
            "date": date_str
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

    response = vk.wall.getComments(
        owner_id=owner_id, post_id=post_id, need_likes=1, count=100
    )
    comments = response["items"]

    for comment in comments:
        if comment["text"] == "":
            continue
        # Сохраняем комментарий
        date_str = datetime.datetime.fromtimestamp(comment["date"]).strftime("%d-%m-%Y")
        comment_info = {
            "comment_id": comment["id"],
            "text": comment["text"],
            "likes": comment["likes"]["count"],
            "reply_to": None,
            "date": date_str,
        }
        comments_info.append(comment_info)

        # Сохраняем ответы к комментарию
        comments_info.extend(get_replies(vk_session, owner_id, post_id, comment["id"]))
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
    response = vk.wall.getComments(
        owner_id=owner_id,
        post_id=post_id,
        comment_id=comment_id,
        need_likes=1,
        count=100,
    )
    replies = response["items"]
    for reply in replies:
        if reply["text"] == "":
            continue

        reply_info = {
            "comment_id": reply["id"],
            "text": reply["text"],
            "likes": reply["likes"]["count"],
            "reply_to" : comment_id,
            "date": reply["date"],
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
        post_info["comments"] = get_comments(vk_session, owner_id, post_id)
        return json.dumps(
            post_info, ensure_ascii=False
        )  # Возвращаем в формате JSON с поддержкой кириллицы

    return None


def parse_vk(vk_session, domain, start_date, end_date, limit=-1):
    """
    Парсит данные о постах и их комментариях на определенном диапазоне дат.

    :param vk_session: Сессия VkApi.
    :param domain: Домен страницы с группой или публичным профилем в VK.
    :param start_date: Начальная дата диапазона для поиска постов (формат "YYYY-MM-DD").
    :param end_date: Конечная дата диапазона для поиска постов (формат "YYYY-MM-DD").
    :param limit: Ограничение количества постов для парсинга (для отладки).
    :return: Список строк JSON с информацией о постах и комментариях.
    """
    owner_id = get_owner_id(vk_session, domain)
    post_ids = get_post_ids(vk_session,domain, start_date, end_date)
    if limit > 0:
        post_ids = post_ids[:limit]
    parsed_posts = []
    for _id in tqdm(post_ids):
        parsed_posts.append(get_post_data(vk_session, owner_id, _id))
    return parsed_posts