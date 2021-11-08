#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# * название источника;
# * наименование новости;
# * ссылку на новость;
# * дата публикации.
# 2. Сложить собранные новости в БД

import requests
from pymongo import MongoClient, ASCENDING, errors as mdb_errors
from lxml import html
from pprint import pprint
from unicodedata import normalize

BASE_URL = 'https://yandex.ru/news'
HEADERS = {
    'User-Agent': 'Chrome/95.0.4638.54 Safari/537.36'
}

DATA_SET = []


def parse_yandex_news():
    data = []
    response = requests.get(url=BASE_URL, headers=HEADERS)

    if not response.ok:
        exit(1)

    root = html.fromstring(response.text)
    blocks = root.xpath(
        "//div[contains(@class, 'mg-grid__row mg-grid__row_gap_8 news-top-flexible-stories') or "
        "contains(@class, 'mg-grid__row mg-grid__row_gap_8 mg-top-rubric-flexible-stories')]")
    for block in blocks:
        news = block.xpath(".//div[contains(@class, 'mg-grid__col mg-grid__col_xs_')]")
        for item in news:
            title = item.xpath(".//h2[@class='mg-card__title']/text()")
            link = item.xpath(".//a[contains(@class, 'mg-card__link')]/@href")
            source = item.xpath(".//a[@class='mg-card__source-link']/@aria-label")
            timestamp = item.xpath(".//span[@class='mg-card-source__time']/text()")

            data.append({
                'title': normalize('NFKD', title[0]).strip(),
                'link': link[0],
                'source': source[0].split(':')[-1].strip(),
                'timestamp': timestamp[0]
            })

    return data


def upload_data_to_mongodb(data):
    mongodb_host = 'localhost'
    mongodb_port = '27017'
    mongodb_user = 'root'
    mongodb_password = 'password'

    database_name = 'gb-data-scraping'
    table_name = 'news'

    mongo = MongoClient(f'mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}')

    db_list = mongo.list_database_names()
    if database_name in db_list:
        mongo.drop_database(database_name)

    db = mongo[database_name]
    table = db[table_name]

    table.create_index([("title", ASCENDING), ("source", ASCENDING)], unique=True)

    try:
        table.insert_many(data, ordered=False)
    except mdb_errors.BulkWriteError as e:
        pprint(e.details['writeErrors'])


if __name__ == '__main__':
    data = parse_yandex_news()
    upload_data_to_mongodb(data)
