import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse


class Crawler:
    def __init__(self):
        self.base_url = 'https://www.sports.ru'
        self.request_url = 'https://www.sports.ru/football/news/'
        self.class_attribute = 'short-text'
        self.pages_folder_name = os.path.dirname(__file__) + '/pages'
        self.index_file_name = os.path.dirname(__file__) + '/index.txt'
        os.mkdir(self.pages_folder_name)

    def find_pages(self):
        page = urllib.request.urlopen(self.request_url)
        soup = BeautifulSoup(page, 'html.parser')
        links = []
        for link in soup.findAll('a', {'class': self.class_attribute}, href=True):
            if link.get('href')[0] == '/':
                link = urllib.parse.urljoin(self.base_url, link.get('href'))
                links.append(link)
        return links

    def download_pages(self, count: int = 100):
        links = list(set(self.find_pages()))
        index_file = open(self.index_file_name, 'w', encoding='utf-8')
        i = 1
        for link in links:
            if i <= count:
                response = requests.get(link)
                if response.status_code == 200:
                    page_name = self.pages_folder_name + '/выкачка_' + str(i) + '.html'
                    with open(page_name, 'w', encoding='utf-8') as page:
                        page.write(response.text)
                    index_file.write(str(i) + ' ' + link + '\n')
                    i += 1
            else:
                break
        index_file.close()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.download_pages()