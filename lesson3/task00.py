#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pprint import pprint
import pymongo.errors
from pymongo import MongoClient, ASCENDING

MONGODB_HOST = 'localhost'
MONGODB_PORT = '27017'
MONGODB_USER = 'root'
MONGODB_PASSWORD = 'password'

DATABASE_NAME = 'gb-data-scraping'
TABLE_NAME = 'salaries'

DATA_FILE = 'output.json'

mongo = MongoClient(f'mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}')
db = None
table = None


def init_database():
    db_list = mongo.list_database_names()
    if DATABASE_NAME in db_list:
        mongo.drop_database(DATABASE_NAME)

    global db
    db = mongo[DATABASE_NAME]
    global table
    table = db[TABLE_NAME]

    table.create_index([("job_name", ASCENDING), ("job_link", ASCENDING), ("job_salary_min", ASCENDING),
                        ("job_salary_max", ASCENDING), ("currency", ASCENDING), ("source_page", ASCENDING)],
                       unique=True)


def load_data():
    with open(DATA_FILE, 'r') as data_file:
        salaries = json.load(data_file)

    for salary in salaries:
        try:
            table.insert_one(salary)
        except pymongo.errors.DuplicateKeyError as e:
            print('Error: found duplicated item')
            print(f'Error: {e}')
        except Exception as e:
            print(f'Fatal error: {e}')


def search_mongo():
    salary = int(input('Enter a salary for searching: ')) or 200000
    currency = input('Enter a currency: ') or 'KZT'

    query = {
        '$and': [
            {
                '$or': [
                    {
                        '$and': [
                            {
                                'job_salary_max': None
                            },
                            {
                                'job_salary_min': {
                                    '$gt': salary
                                }
                            }
                        ]
                    },
                    {
                        '$and': [
                            {
                                'job_salary_min': None
                            },
                            {
                                'job_salary_max': {
                                    '$gt': salary
                                }
                            }
                        ]
                    }
                ]
            },
            {
                'currency': currency
            }
        ]
    }

    result = table.find(query)
    for row in result:
        pprint(row)


if __name__ == '__main__':
    init_database()
    load_data()
    search_mongo()
