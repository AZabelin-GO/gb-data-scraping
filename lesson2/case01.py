#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Вариант 1 Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы
# получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько
# страниц сайта (также вводим через input или аргументы).
#
# Получившийся список должен содержать в себе минимум:
# 1. Наименование вакансии.
# 2. Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# 3. Ссылку на саму вакансию.
# 4. Сайт, откуда собрана вакансия.
#
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
# Сохраните в json либо csv.

import re
import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from requests.utils import requote_uri


def parse_hh(job_name, pages_count=1):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}

    result = []

    for i in range(pages_count):
        search_url = f'https://hh.ru/search/vacancy?text={job_name}&page={i}'
        response = requests.get(search_url, headers=headers)
        if response.ok:
            soup = bs(response.content, 'html.parser')
            jobs = soup.find_all('div', {'class': "vacancy-serp-item"})
            for job in jobs:
                tmp = job.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
                job_name = tmp.getText()
                job_link = tmp.get('href')
                tmp = job.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                if tmp:
                    salaries = [int(x) for x in re.findall(r'[0-9]+', ("".join(tmp.getText().split())))]
                    currency = tmp.getText().split()[-1]
                    if len(salaries) > 1:
                        job_salary_min = salaries[0]
                        job_salary_max = salaries[1]
                    else:
                        job_salary_min = salaries[0]
                        job_salary_max = None
                result.append({
                    'job_name': job_name,
                    'job_link': job_link,
                    'job_salary_min': job_salary_min,
                    'job_salary_max': job_salary_max,
                    'currency': currency,
                    'source_page': requote_uri(search_url)
                })
        else:
            break

    pprint(result)
    with open('output.json', 'w') as file:
        file.write(json.dumps(result, indent=2))
        print()
        pprint('See results in "output.json"')


if __name__ == '__main__':
    vacancy = str(input('Enter a vacancy for search. default is "python": ')) or 'python'
    pages = input('Enter a number of pages for scraping. Default is "1": ') or 1
    parse_hh(vacancy, int(pages))
