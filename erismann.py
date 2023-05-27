import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import os

requests.packages.urllib3.disable_warnings()
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36 '
}

url = 'https://erismann.ru'
catalogurl = 'https://erismann.ru/product/all-collections/'

if not os.path.exists(Path('data/images')):
    Path('data/images').mkdir(parents=True)

result = requests.get(url=catalogurl, verify=False, headers=headers)
if result.status_code == 200:
    soup = BeautifulSoup(result.text, 'lxml')
    image_dct = []

    # find all items
    items = soup.find_all('div', class_='item')
    print(f'Найдено {len(items)} коллекций.')

    for item in items:
        link = url + item.find(class_='img').get('href')
        collection = item.find(class_='name').get_text().strip()
        result = requests.get(url=link, verify=False, headers=headers)
        soup = BeautifulSoup(result.text, 'lxml')

        products = soup.find_all(class_='product-item')
        print(f'Загружается коллекция {collection}.')

        for product in products:
            link = url + product.find('a').get('href').strip()

            result = requests.get(url=link, verify=False, headers=headers)
            soup = BeautifulSoup(result.text, 'lxml')
            # collection = soup.find(class_='p-name').get_text().strip()
            model = soup.find(class_='p-article').get_text().split()[-1]

            # find all images for model
            all_image = soup.find(class_='image').find_all('a', href=True)

            for image in all_image:
                imgurl = url + image.get('href')
                name = imgurl.split('/')[-1]
                res = requests.get(url=imgurl, headers=headers, verify=False)
                content = res.content
                image_dct.append({name: (model, collection)})
                with open(Path(f'data/images/{name}'), 'wb') as file:
                    file.write(content)

    with open(Path('catalog/erismann.json'), 'w', encoding='utf-8') as file:
        json.dump(image_dct, file, indent=4, ensure_ascii=False)
else:
    print(f'Error {result.status_code}')
