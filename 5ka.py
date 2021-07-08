import requests
import time
import json


class Parser5ka:
    _domain = 'https://5ka.ru'
    _api_path = '/api/v2/special_offers/'
    _api_cat_path = '/api/v2/categories/'
    categories = []
    params = {
        'records_per_page': 20,
        'categories': '',
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    }
    __to_replace = (',', '-', '/', '\\', '.', '"', "'", '*', '#',)

    def __init__(self):
        self.products = []

    def download_cat(self):
        url = self._domain + self._api_cat_path
        response = requests.get(url, headers=self.headers)
        self.categories = response.json()

    def replace_to_name(self, name):
        for itm in self.__to_replace:
            name = name.replace(itm, '')
        return '_'.join(name.split()).lower()

    def download(self):
        params = self.params
        url = self._domain + self._api_path

        while url:
            for cat in self.categories:
                params['categories'] = cat['parent_group_code']
                response = requests.get(url, headers=self.headers, params=params)
                data = response.json()
                with open(self.replace_to_name(cat['parent_group_name'])+'.json', 'w', encoding='UTF-8') as file:
                    json.dump(data, file, ensure_ascii=False)
                params = {}
                time.sleep(0.1)


if __name__ == '__main__':
    parser = Parser5ka()
    parser.download_cat()
    parser.download()
    print(1)
