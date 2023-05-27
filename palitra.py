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

url = 'https://oboi-palitra.ru'
catalogurl = 'https://oboi-palitra.ru/oboi'
pagenurl = 'https://oboi-palitra.ru/oboi/?PAGEN_1='

if not os.path.exists(Path('data/images')):
    Path('data/images').mkdir(parents=True)

result = requests.get(url=catalogurl, verify=False, headers=headers)
if result.status_code == 200:
    soup = BeautifulSoup(result.text, 'lxml')

    # find count of page
    cnt_page = int(soup.find_all('ul', class_='claims-pager')[-1].
                   find_all('a', href=True)[-1].get('href').split('=')[-1])

    image_dct = []

    for page in range(1, cnt_page + 1):
        print(f'{page} страница каталога из {cnt_page} страниц.')
        result = requests.get(url=f'{pagenurl}{page}', verify=False)
        soup = BeautifulSoup(result.text, 'lxml')
        # find all collection and download images for collection
        all_products = soup.find_all('div', class_='col-12 col-md-4 col-xl-3 item-card__card-wrapper')
        print(f'Найдено {len(all_products)} коллекций.')
        for product in all_products:

            # request page of product
            # create new link
            link = url + product.find(class_='item-card__card-full-link').get('href')
            result = requests.get(link, verify=False, headers=headers)
            if result.status_code != 200:
                print(f'Страница {link} не найдена. Error {result.status_code}')
                continue
            soup = BeautifulSoup(result.text, 'lxml')

            # find name collection and model
            collection = soup.find('a', class_='model-caption')
            if collection:
                collection = collection.get_text('\n', strip=True)
            else:
                collection = 'Noname collection'
            print(f'Загружается коллекция {collection}.')
            model = soup.find('div', class_='article-caption prov-text').get_text('\n', strip=True)

            all_image = soup.find_all('div', class_='product-block__grid-item item-col-2')[:]
            for image in all_image:
                imgurl = image.find('img').get('src')
                name = imgurl.split('/')[-1]
                res = requests.get(url=imgurl, headers=headers, verify=False)
                content = res.content
                image_dct.append({name: (model, collection)})
                with open(Path(f'data/images/{name}'), 'wb') as file:
                    file.write(content)

    with open(Path('catalog/palitra.json'), 'w', encoding='utf-8') as file:
        json.dump(image_dct, file, indent=4, ensure_ascii=False)
else:
    print(f'Error {result.status_code}')
