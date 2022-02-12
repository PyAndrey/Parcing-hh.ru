import csv

import requests
from bs4 import BeautifulSoup as BS


class ParseHhru():
    """Парсинг сайта hh.ru."""

    __HEADERS = {'accept': '*/*',
                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    BASE_URL = 'https://hh.ru/search/vacancy?area=1007&search_period=30&text=Программист&page=0'

    def __init__(self):
        self.jobs = []
        self.urls = []

    def hh_parse(self):
        """Достает все дивы с вакансиями на сайте."""
        self.urls.append(self.BASE_URL)
        self.s = requests.Session()
        request = self.s.get(self.BASE_URL, headers=self.__HEADERS)
        if request.status_code == 200:
            soup = BS(request.content, 'lxml')
            try:
                pagination = soup.find_all(
                    'a', attrs={'data-qa': 'pager-page'})
                count = int(pagination[-1].text)
                for i in range(count):
                    url = f'https://hh.ru/search/vacancy?area=1007&search_period=30&text=Программист&page={i}'
                    if url not in self.urls:
                        self.urls.append(url)
            except:
                pass
            for url in self.urls:
                self.bypass_urls(url)

    def bypass_urls(self, url):
        """Находит в каждом url дивы."""
        try:
            request = self.s.get(url, headers=self.__HEADERS)
            soup = BS(request.content, 'lxml')
            div = soup.find_all(
                'div', attrs={'data-qa': 'vacancy-serp__vacancy'})
            div_premium = soup.find_all(
                'div', attrs={'data-qa': 'vacancy-serp__vacancy vacancy-serp__vacancy_premium'})
            divs = div + div_premium
            for div in divs:
                self.bypass_divs(div)
        except:
            pass

    def bypass_divs(self, div):
        """Объединяет весь контент вакансий в список словарей."""
        title = div.find(
            'a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
        href = div.find(
            'a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
        company = div.find(
            'a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
        text1 = div.find(
            'div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
        text2 = div.find(
            'div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
        content = f'{text1} {text2}'
        self.jobs.append({
            'title': title,
            'href': href,
            'company': company,
            'content': content
        })

    def files_writer(self):
        """Запись в файл результатов."""
        self.hh_parse()
        with open('parsed_jobs.csv', 'w', encoding='utf-8') as file:
            a_pen = csv.writer(file)
            a_pen.writerow(('Вакансия', 'URL', 'Компания', 'Описание'))
            for job in self.jobs:
                a_pen.writerow((job['title'], job['href'],
                                job['company'], job['content']))


if __name__ == "__main__":
    ParseHhru().files_writer()
